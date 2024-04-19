import aiohttp
import json
import jsonschema
import schemas
from aio_pika import connect_robust, Message

API_KEY = "RGAPI-4526512a-99f9-457a-be29-389f54020c2c"
ENDPOINTS = {
    "ACC_BY_RIOT_ID": "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/",
    "CHALL_ACCS": "https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I",
    "MATCH_BY_ID": "https://europe.api.riotgames.com/lol/match/v5/matches/",
    "MATCHES_BY_PUUID": "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/",
    "ACC_BY_SUMM_ID": "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/"
}

class RabbitMQClient:
    def __init__(self, loop, redisObj):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        self.redisObj = redisObj
        # Start the consumer automatically
        self.loop.create_task(self.consume())

    def get_last_10_json(self, user_id):
        # Use LRANGE to get the last 10 elements of the list
        records = self.redisObj.lrange(f'user:{user_id}:records', 0, 9)
        # Convert the strings back to JSON objects
        return [json.loads(record) for record in records]

    def store_last_10_json(self, user_id, json_object):
        # Convert the JSON object to a string
        json_str = json.dumps(json_object)
        
        # LPUSH adds the new JSON object to the beginning of the list
        # LTRIM trims the list to the last 10 elements
        self.redisObj.lpush(f'user:{user_id}:records', json_str)
        self.redisObj.ltrim(f'user:{user_id}:records', 0, 9)

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

    async def validate_message(self, action, schema):
        try:
            #message_data = json.loads(action)
            jsonschema.validate(instance=action, schema=schema)
            print("Message is valid.")
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Message is invalid: {e}")
            return False
        except json.JSONDecodeError:
            print("Message is not a valid JSON.")
            return False

    async def process_incoming_message(self, message):
        
        msg = message.body.decode()
        msg_json = json.loads(msg)
        
        if not await self.validate_message(msg_json, schemas.action_schema):
            return
        
        action = msg_json['action']

        if action == "ACC_BY_RIOT_ID":
            params = [msg_json['gameName'], msg_json['tagLine']]
            data = await self.fetch_data_from_api("ACC_BY_RIOT_ID", params)
        elif action == "MATCHES_BY_RIOT_ID":
            params = [msg_json['gameName'], msg_json['tagLine']]
            acc = await self.fetch_data_from_api("ACC_BY_RIOT_ID", params)

            if self.redisObj.exists(acc['puuid']):
                data = self.get_last_10_json(acc['puuid'])
            else:
                data = await self.fetch_data_from_api("MATCHES_BY_PUUID", [acc['puuid']])
            
            for match in data:
                self.store_last_10_json(acc['puuid'], match)
        elif action == "REFRESH_MATCHES_BY_RIOT_ID":
            params = [msg_json['gameName'], msg_json['tagLine']]
            acc = await self.fetch_data_from_api("ACC_BY_RIOT_ID", params)
            data = await self.fetch_data_from_api("MATCHES_BY_PUUID", [acc['puuid']])

            for match in data:
                self.store_last_10_json(acc['puuid'], match)
        elif action == "NEXT_20_MATCHES":
            params = [msg_json['gameName'], msg_json['tagLine']]
            acc = await self.fetch_data_from_api("ACC_BY_RIOT_ID", params)
            data = await self.fetch_data_from_api("MATCHES_BY_PUUID", [acc['puuid'], msg_json['matchStartIndex']])
        elif action == "CHALL_ACCS":
            data = await self.fetch_data_from_api("CHALL_ACCS")
        elif action == "ACC_BY_SUMM_ID":
            params = [msg_json['summId']]
            data = await self.fetch_data_from_api("ACC_BY_SUMM_ID", params)
        elif action == "MATCHES_BY_PUUID":
            params = [msg_json['puuid']]
            data = await self.fetch_data_from_api("MATCHES_BY_PUUID", params)

        if not await self.validate_message(data, schemas.reply_schema):
            return

        await self.send_data_to_queue(data)
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)