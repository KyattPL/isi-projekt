import json
import jsonschema
import schemas
from aio_pika import connect_robust, Message

class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queues = {}
        self.loop.create_task(self.consume())

    async def connect_and_consume(self):
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queues["lol.data.reply"] = await self.channel.declare_queue("lol.data.reply", durable=False)
        # self.queues["lol.data.request"] = await self.channel.declare_queue("lol.data.request", durable=False)
        await self.queues["lol.data.reply"].consume(lambda msg: self.process_incoming_message(msg, schemas.riot_service_reply_schema), no_ack=False)
        return self.connection

    async def validate_message(self, action, schema):
        try:
            jsonschema.validate(instance=action, schema=schema)
            print("Message is valid.")
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Message is invalid: {e}")
            return False
        except json.JSONDecodeError:
            print("Message is not a valid JSON.")
            return False

    async def process_incoming_message(self, message, schema):
        
        msg = message.body.decode()
        msg_json = json.loads(msg)
        
        if not await self.validate_message(msg_json, schema):
            return
        
        #print(msg_json)
        # action = msg_json['action']

        # await self.send_data_to_queue(data)
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()

    async def send_data_to_riot_service(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)

        if not await self.validate_message(data, schemas.riot_service_request_schema):
            return

        await self.channel.default_exchange.publish(message, routing_key="lol.data.request")