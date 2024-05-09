import aiohttp
import json
import jsonschema
import logging
import schemas
from aio_pika import connect_robust, Message

import request_actions as RA
from request_actions import ActionType

logger = logging.getLogger(__name__)
logging.basicConfig(filename="riot-service.log",
                    level=logging.INFO, filemode='w')

API_KEY = "RGAPI-4eeb1332-8bfe-4b0f-bd72-9a1e232b41b3"

ENDPOINTS = {
    ActionType.ACC_BY_RIOT_ID: "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/",
    ActionType.CHALL_ACCS: "https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I",
    ActionType.MATCH_DATA_BY_MATCH_ID: "https://europe.api.riotgames.com/lol/match/v5/matches/",
    ActionType.MATCHES_BY_PUUID: "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/",
    ActionType.ACC_BY_SUMM_ID: "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/"
}


class RabbitMQClient:
    def __init__(self, loop, redisObj):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        self.redisObj = redisObj
        self.loop.create_task(self.consume())

    def get_last_10_json(self, user_id):
        records = self.redisObj.lrange(f'user:{user_id}:records', 0, 9)
        return [json.loads(record) for record in records]

    def store_last_10_json(self, user_id, json_object):
        json_str = json.dumps(json_object)

        self.redisObj.lpush(f'user:{user_id}:records', json_str)
        self.redisObj.ltrim(f'user:{user_id}:records', 0, 9)

    async def fetch_data_from_api(self, action, urlParams=None, queryParams=""):
        async with aiohttp.ClientSession() as session:
            params_str = ""
            if urlParams is not None:
                for (index, p) in enumerate(urlParams):
                    params_str += p
                    if index < len(urlParams) - 1:
                        params_str += "/"

            if action == ActionType.MATCHES_BY_PUUID:
                params_str += "/ids"

            urlEnding = f"&{queryParams}" if queryParams != "" else ""

            logger.info(
                f'{ENDPOINTS[action]}{params_str}?api_key={API_KEY}{urlEnding}')

            async with session.get(f'{ENDPOINTS[action]}{params_str}?api_key={API_KEY}{urlEnding}') as response:
                data = await response.json()
                return data

    async def send_data_to_queue(self, data, reply_to):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)
        await self.channel.default_exchange.publish(message, routing_key=reply_to)

    async def connect_and_consume(self):
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("lol.data.request", durable=False)
        await self.queue.consume(self.process_incoming_message, no_ack=False)
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

    def get_strategy(self, action):
        strategies = {
            ActionType.ACC_BY_RIOT_ID: RA.AccByRiotIdStrategy(),
            ActionType.MATCHES_BY_RIOT_ID: RA.MatchesByRiotIdStrategy(),
            ActionType.REFRESH_MATCHES_BY_RIOT_ID: RA.RefreshMatchesByRiotIdStrategy(),
            ActionType.NEXT_10_MATCHES: RA.Next10MatchesStrategy(),
            ActionType.CHALL_ACCS: RA.ChallAccsStrategy(),
            ActionType.ACC_BY_SUMM_ID: RA.AccBySummIdStrategy(),
            ActionType.MATCHES_BY_PUUID: RA.MatchesByPuuidStrategy(),
            ActionType.MATCHES_BY_PUUID_24HRS: RA.MatchesByPuuid24HStrategy(),
            ActionType.MATCH_DATA_BY_MATCH_ID: RA.MatchDataByMatchIdStrategy(),
            ActionType.NEW_SNAPSHOT_REQUEST: RA.NewSnapshotRequestStrategy()
        }
        return strategies.get(action, None)

    async def process_incoming_message(self, message):
        msg = message.body.decode()
        msg_json = json.loads(msg)

        if not await self.validate_message(msg_json, schemas.action_schema):
            logger.error("Invalid message received. Rejecting.")
            await message.reject()
            return

        action = ActionType(msg_json['action'])
        strategy = self.get_strategy(action)

        if strategy is None:
            logger.error(f"No strategy found for action: {action.value}")
            await message.reject()
            return

        data = await strategy.execute(self, msg_json)

        if not await self.validate_message(data, schemas.reply_schema):
            logger.error("Invalid data generated. Rejecting.")
            await message.reject()
            return

        await self.send_data_to_queue(data, message.reply_to)
        await message.ack()

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)
