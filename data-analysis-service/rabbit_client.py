import datetime
import json
import jsonschema
import jsonschema.exceptions
import logging
import schemas

from aio_pika import connect_robust, Message

import database as db

logger = logging.getLogger(__name__)
logging.basicConfig(filename='data-analysis-service.log',
                    level=logging.INFO, filemode='w')


class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queues = {}
        self.loop.create_task(self.consume())
        self.response = None

    async def connect_and_consume(self):
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queues["lol.data.reply.analysis"] = await self.channel.declare_queue("lol.data.reply.analysis", durable=False)
        self.queues["analysis.request"] = await self.channel.declare_queue("analysis.request", durable=False)
        await self.queues["lol.data.reply.analysis"].consume(self.process_riot_service_message, no_ack=False)
        await self.queues["analysis.request"].consume(self.process_web_service_message, no_ack=False)
        return self.connection

    async def validate_message(self, action, schema):
        try:
            jsonschema.validate(instance=action, schema=schema)
            logger.info("Message is valid.")
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Message is invalid: {e}")
            return False
        except json.JSONDecodeError:
            logger.error("Message is not a valid JSON.")
            return False

    async def process_riot_service_message(self, message):
        msg = message.body.decode()
        msg_json = json.loads(msg)

        if not await self.validate_message(msg_json, schemas.riot_service_reply_schema):
            logging.error("Received invalid message. Ignoring.")
            await message.reject(requeue=False)
            return

        await self.insert_matches_into_db(msg_json)
        await self.send_data_to_web_service(db.get_snapshot())

        await message.ack()

    async def consume(self):
        await self.connect_and_consume()

    async def send_data_to_riot_service(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(
            body=data_bytes, reply_to=self.queues["lol.data.reply.analysis"].name)

        if not await self.validate_message(data, schemas.riot_service_request_schema):
            logging.error("Message is invalid. Not sending to Riot service.")
            return

        await self.channel.default_exchange.publish(message, routing_key="lol.data.request")

    async def process_web_service_message(self, message):
        msg = message.body.decode()
        msg_json = json.loads(msg)

        if not await self.validate_message(msg_json, schemas.web_service_request_schema):
            logging.error("Received invalid message. Ignoring.")
            await message.reject(requeue=False)
            return

        await message.ack()

    async def send_data_to_web_service(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)

        if not await self.validate_message(data, schemas.web_service_reply_schema):
            logging.error("Message is invalid. Not sending to Web service.")
            return

        await self.channel.default_exchange.publish(message, routing_key="analysis.reply")

    async def insert_matches_into_db(self, matches):
        with open("last_snapshot_info.json", 'r') as file:
            data = json.load(file)

        snapshotId = data['snapshotId']

        db.create_matches_table()

        for match in matches:
            if match['info']['endOfGameResult'] == "Abort_Unexpected":
                continue

            patch = match['info']['gameVersion'].split('.')
            patch = patch[0] + '.' + patch[1]
            gameDuration = match['info']['gameDuration']
            participants = match['info']['participants']

            for p in participants:
                db.insert_match(snapshotId+1, patch, gameDuration, p['championName'], p['kills'], p['deaths'], p['assists'],
                                p['champExperience'], p['goldEarned'], p['totalDamageDealtToChampions'], p['totalDamageTaken'],
                                p['totalHeal'], p['totalMinionsKilled'], p['visionScore'], p['win'])

        db.create_snapshot_table()

        avg_per_champ = db.calculate_avg_per_champion(snapshotId+1)

        for champion, avg_data in avg_per_champ.items():
            db.insert_snapshot(
                champion,
                avg_data['avg_kills'],
                avg_data['avg_deaths'],
                avg_data['avg_assists'],
                avg_data['avg_champExperience'],
                avg_data['avg_goldEarned'],
                avg_data['avg_totalDamageDealtToChampions'],
                avg_data['avg_totalDamageTaken'],
                avg_data['avg_totalHeal'],
                avg_data['avg_totalMinionsKilled'],
                avg_data['avg_visionScore']
            )

        with open("last_snapshot_info.json", 'w') as file:
            json.dump({'snapshotId': snapshotId+1,
                       'timeOfLastSnapshot': json.dumps(datetime.datetime.now().isoformat())}, file, indent=4)
