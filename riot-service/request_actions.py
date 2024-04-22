from enum import Enum

class ActionType(Enum):
    ACC_BY_RIOT_ID = "ACC_BY_RIOT_ID"
    MATCHES_BY_RIOT_ID = "MATCHES_BY_RIOT_ID"
    REFRESH_MATCHES_BY_RIOT_ID = "REFRESH_MATCHES_BY_RIOT_ID"
    NEXT_20_MATCHES = "NEXT_20_MATCHES"
    CHALL_ACCS = "CHALL_ACCS"
    ACC_BY_SUMM_ID = "ACC_BY_SUMM_ID"
    MATCHES_BY_PUUID = "MATCHES_BY_PUUID"
    MATCHES_BY_PUUID_24HRS = "MATCHES_BY_PUUID_24HRS"
    MATCH_DATA_BY_MATCH_ID = "MATCH_DATA_BY_MATCH_ID"

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
        acc = await client.fetch_data_from_api(ActionType.MATCHES_BY_RIOT_ID, params)

        if client.redisObj.exists(acc['puuid']):
            data = client.get_last_10_json(acc['puuid'])
        else:
            data = await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [acc['puuid']], "type=ranked")
        
        for match in data:
            client.store_last_10_json(acc['puuid'], match)
        
        return data
    
class RefreshMatchesByRiotIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['gameName'], msg_json['tagLine']]
        acc = await client.fetch_data_from_api(ActionType.ACC_BY_RIOT_ID, params)
        data = await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [acc['puuid']], "type=ranked")

        for match in data:
            client.store_last_10_json(acc['puuid'], match)

        return data
    
class Next20MatchesStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['gameName'], msg_json['tagLine']]
        acc = await client.fetch_data_from_api(ActionType.ACC_BY_RIOT_ID, params)
        return await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, [acc['puuid']], f"type=ranked&start={msg_json['matchStartIndex']}")
    
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
        return await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, params, "type=ranked")
    
class MatchesByPuuid24HStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['puuid']]
        return await client.fetch_data_from_api(ActionType.MATCHES_BY_PUUID, params, f"type=ranked&startTime={msg_json['snapshotTimeThreshold']}")
    
class MatchDataByMatchIdStrategy(ActionStrategy):
    async def execute(self, client, msg_json):
        params = [msg_json['matchId']]
        return await client.fetch_data_from_api(ActionType.MATCH_DATA_BY_MATCH_ID, params)