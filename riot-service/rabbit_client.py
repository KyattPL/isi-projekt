import aiohttp
import json
import jsonschema
import schemas
from aio_pika import connect_robust, Message

API_KEY = "RGAPI-153f72e3-dfbf-41b6-8929-1be5d2bc46f6"
ENDPOINTS = {
    "ACC_BY_RIOT_ID": "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/",
    "CHALL_ACCS": "https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I",
    "MATCH_BY_ID": "https://europe.api.riotgames.com/lol/match/v5/matches/",
    "MATCHES_BY_PUUID": "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/",
    "ACC_BY_SUMM_ID": "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/"
}

class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        # Start the consumer automatically
        self.loop.create_task(self.consume())

    async def fetch_data_from_api(self, action, params=None):
        async with aiohttp.ClientSession() as session:
            params_str = ""
            for (index, p) in enumerate(params):
                params_str += p
                if index < len(params) - 1:
                    params_str += "/"

            if action == "MATCHES_BY_PUUID":
                params_str += "/ids"

            #print(f'{ENDPOINTS[action]}{params_str}?api_key={API_KEY}')

            async with session.get(f'{ENDPOINTS[action]}{params_str}?api_key={API_KEY}') as response:
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
        await self.validate_message(msg_json)

        action = msg_json['action']

        if action == "ACC_BY_RIOT_ID":
            params = [msg_json['gameName'], msg_json['tagLine']]
            data = await self.fetch_data_from_api("ACC_BY_RIOT_ID", params)
        elif action == "MATCHES_BY_RIOT_ID":
            params = [msg_json['gameName'], msg_json['tagLine']]
            acc = await self.fetch_data_from_api("ACC_BY_RIOT_ID", params)
            data = await self.fetch_data_from_api("MATCHES_BY_PUUID", [acc['puuid']])
        elif action == "NEW_SNAPSHOT_DATA":
            params = [msg_json['snapshotTimeThreshold']]
            accs = await self.fetch_data_from_api("CHALL_ACCS", [])

            data = set()

            for acc in accs:
                acc_with_puuid = await self.fetch_data_from_api("ACC_BY_SUMM_ID", [acc['summonerId']])
                matches = await self.fetch_data_from_api("MATCHES_BY_PUUID", [acc_with_puuid['puuid']])

                for match in matches:
                    data.add(match)

        #print(data)
        await self.send_data_to_queue(data)
        
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)