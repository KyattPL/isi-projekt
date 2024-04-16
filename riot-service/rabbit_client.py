import aiohttp
import asyncio
import json
import jsonschema
import schemas
from aio_pika import connect_robust, Message

class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        # Start the consumer automatically
        self.loop.create_task(self.consume())

    async def fetch_data_from_api(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://euw1.api.riotgames.com/riot/account/v1/accounts/by-riot-id/KyattPL/EUW?api_key=RGAPI-153f72e3-dfbf-41b6-8929-1be5d2bc46f6') as response:
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
        
        action = message.body.decode()
        await self.validate_message(action)

        if action == "fetch_data":
            data = await self.fetch_data_from_api()
            await self.send_data_to_queue(data)
        
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)

# Example usage
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     rabbit_client = RabbitMQClient(loop)
#     try:
#         loop.run_forever()
#     except KeyboardInterrupt:
#         print("Closing RabbitMQ client...")
#         loop.run_until_complete(rabbit_client.connection.close())
#         loop.close()