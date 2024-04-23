import asyncio
import json
import jsonschema
import jsonschema.exceptions
import schemas
from aio_pika import connect_robust, Message
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='data-analysis-service.log', level=logging.INFO)

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

        self.response = msg_json
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()

    async def send_data_to_riot_service(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes, reply_to=self.queues["lol.data.reply.analysis"].name)

        if not await self.validate_message(data, schemas.riot_service_request_schema):
            logging.error("Message is invalid. Not sending to Riot service.")
            return

        await self.channel.default_exchange.publish(message, routing_key="lol.data.request")

        while self.response is None:
          await asyncio.sleep(0.1)

        if not await self.validate_message(self.response, schemas.riot_service_reply_schema):
            logging.error("Response from Riot service is invalid.")
            return

        resp = self.response
        self.response = None
        return resp

    async def process_web_service_message(self, message):
        msg = message.body.decode()
        msg_json = json.loads(msg)
        
        if not await self.validate_message(msg_json, schemas.web_service_request_schema):
            logging.error("Received invalid message. Ignoring.")
            await message.reject(requeue=False)
            return

        # self.response = msg_json
        await message.ack()

    async def send_data_to_web_service(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)

        if not await self.validate_message(data, schemas.web_service_reply_schema):
            logging.error("Message is invalid. Not sending to Web service.")
            return

        await self.channel.default_exchange.publish(message, routing_key="analysis.reply")

        # while self.response is None:
        #   await asyncio.sleep(0.1)

        # if not await self.validate_message(self.response, schemas.riot_service_reply_schema):
        #     logging.error("Response from Web service is invalid.")
        #     return

        # resp = self.response
        # self.response = None
        # return resp
