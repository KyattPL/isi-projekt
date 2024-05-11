import asyncio
import datetime
from enum import Enum
from datetime import datetime as dt


class ActionType(Enum):
    ACC_BY_RIOT_ID = "ACC_BY_RIOT_ID"
    MATCHES_BY_RIOT_ID = "MATCHES_BY_RIOT_ID"
    REFRESH_MATCHES_BY_RIOT_ID = "REFRESH_MATCHES_BY_RIOT_ID"
    NEXT_10_MATCHES = "NEXT_10_MATCHES"
    CHALL_ACCS = "CHALL_ACCS"
    ACC_BY_SUMM_ID = "ACC_BY_SUMM_ID"
    MATCHES_BY_PUUID = "MATCHES_BY_PUUID"
    MATCHES_BY_PUUID_24HRS = "MATCHES_BY_PUUID_24HRS"
    MATCH_DATA_BY_MATCH_ID = "MATCH_DATA_BY_MATCH_ID"
    NEW_SNAPSHOT_REQUEST = "NEW_SNAPSHOT_REQUEST"


class ActionStrategy:
    async def execute(self, client, msg_json):
        pass


class AccByRiotIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['gameName'], msg_json['tagLine']]
        return await client.fetch_data_from_api(ActionType.ACC_BY_RIOT_ID, params)


class MatchesByRiotIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['gameName'], msg_json['tagLine']]
        acc = await client.fetch_data_from_api(ActionType.ACC_BY_RIOT_ID, params)

        if client.redisObj.exists(acc['puuid']):
            data = client.get_last_10_json(acc['puuid'])
        else:
            data = await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [acc['puuid']], "type=ranked&count=10")

        for match in data:
            client.store_last_10_json(acc['puuid'], match)

        return data


class RefreshMatchesByRiotIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['gameName'], msg_json['tagLine']]
        acc = await client.fetch_data_from_api(ActionType.ACC_BY_RIOT_ID, params)
        data = await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [acc['puuid']], "type=ranked&count=10")

        for match in data:
            client.store_last_10_json(acc['puuid'], match)

        return data


class Next10MatchesStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['gameName'], msg_json['tagLine']]
        acc = await client.fetch_data_from_api(ActionType.ACC_BY_RIOT_ID, params)
        return await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [acc['puuid']], f"type=ranked&start={msg_json['matchStartIndex']}&count=10")


class ChallAccsStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        return await client.fetch_data_from_api(ActionType.CHALL_ACCS)


class AccBySummIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['summId']]
        return await client.fetch_data_from_api(ActionType.ACC_BY_SUMM_ID, params)


class MatchesByPuuidStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['puuid']]
        return await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, params, "type=ranked&count=10")


class MatchesByPuuid24HStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['puuid']]
        return await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, params, f"type=ranked&startTime={msg_json['snapshotTimeThreshold']}&count=10")


class MatchDataByMatchIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['matchId']]
        return await client.fetch_data_from_api(ActionType.MATCH_DATA_BY_MATCH_ID, params)


class NewSnapshotRequestStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        challs = await client.fetch_data_from_api(ActionType.CHALL_ACCS)
        challs = challs[:90]

        accs_puuids = []
        for acc in challs:
            resp = await client.fetch_data_from_api(ActionType.ACC_BY_SUMM_ID, [acc['summonerId']])
            accs_puuids.append(resp['puuid'])

        await asyncio.sleep(120)

        print("here")

        start_date = dt.strptime('16/06/2021', '%d/%m/%Y')
        yesterday = dt.now() - datetime.timedelta(days=1)
        seconds_passed = int((yesterday - start_date).total_seconds())

        match_ids = set()
        for puuid in accs_puuids:
            resp = await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [puuid], f"type=ranked&startTiime={seconds_passed}&count=10")
            for match in resp:
                match_ids.add(match)

        matches_data = []
        index = 0
        for match_id in match_ids:
            if index % 95 == 0:
                await asyncio.sleep(120)
            resp = await client.fetch_data_from_api(ActionType.MATCH_DATA_BY_MATCH_ID, [match_id])
            matches_data.append(resp)
            index += 1

        return matches_data
