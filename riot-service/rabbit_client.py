import aiohttp
import json
import jsonschema
import schemas
from aio_pika import connect_robust, Message

API_KEY = "RGAPI-153f72e3-dfbf-41b6-8929-1be5d2bc46f6"
ENDPOINTS = {
    "ACC_BY_RIOT_ID": "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
}


class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        # Start the consumer automatically
        self.loop.create_task(self.consume())

    async def fetch_data_from_api(self, endpoint, params=None):
        async with aiohttp.ClientSession() as session:
            params_str = ""
            for (index, p) in enumerate(params):
                params_str += p
                if index < len(params) - 1:
                    params_str += "/"

            print(f'{endpoint}{params_str}?api_key={API_KEY}')

            async with session.get(f'{endpoint}{params_str}?api_key={API_KEY}') as response:
                data = await response.json()
                return data

    async def send_data_to_queue(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)
        await self.channel.default_exchange.publish(message, routing_key="lol.data.reply")

    async def connect_and_consume(self):
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("lol.data.request", durable=False)
        await self.queue.consume(self.process_incoming_message, no_ack=False)
        return self.connection

    async def validate_message(self, action):
        try:
            #message_data = json.loads(action)
            jsonschema.validate(instance=action, schema=schemas.action_schema)
            print("Message is valid.")
        except jsonschema.exceptions.ValidationError as e:
            print(f"Message is invalid: {e}")
        except json.JSONDecodeError:
            print("Message is not a valid JSON.")

    async def process_incoming_message(self, message):
        
        msg = message.body.decode()
        msg_json = json.loads(msg)
        print(msg_json)

        await self.validate_message(msg_json)

        action = msg_json['action']

        if action == "ACC_BY_RIOT_ID":
            params = [msg_json['gameName'], msg_json['tagLine']]
        else:
            params = []


        data = await self.fetch_data_from_api(ENDPOINTS[action], params)
        print(data)
        await self.send_data_to_queue(data)
        
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)