action_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["ACC_BY_RIOT_ID", "MATCHES_BY_RIOT_ID", "REFRESH_MATCHES_BY_RIOT_ID", "NEXT_10_MATCHES", "CHALL_ACCS", "ACC_BY_SUMM_ID", "MATCHES_BY_PUUID", "MATCHES_BY_PUUID_24HRS", "MATCH_DATA_BY_MATCH_ID"]},
        "gameName": {"type": "string"},
        "tagLine": {"type": "string"},
        "summId": {"type": "string"},
        "puuid": {"type": "string"},
        "snapshotTimeThreshold": {"type": "integer", "minimum": 0},
        "matchStartIndex": {"type": "integer", "minimum": 0},
        "matchId": {"type": "string"}
    },
    "required": ["action"],
    "anyOf": [
        {
            "if": {
                "properties": {
                    "action": {"enum": ["ACC_BY_RIOT_ID", "MATCHES_BY_RIOT_ID", "REFRESH_MATCHES_BY_RIOT_ID"]}
                }
            },
            "then": {
                "required": ["gameName", "tagLine"]
            }
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "NEXT_10_MATCHES"}
                }
            },
            "then": {
                "required": ["matchStartIndex"]
            }
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "ACC_BY_SUMM_ID"}
                }
            },
            "then": {
                "required": ["summId"]
            }
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "MATCHES_BY_PUUID"}
                }
            },
            "then": {
                "required": ["puuid"]
            }
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "MATCHES_BY_PUUID_24HRS"}
                }
            },
            "then": {
                "required": ["puuid", "snapshotTimeThreshold"]
            }
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "MATCH_DATA_BY_MATCH_ID"}
                }
            },
            "then": {
                "required": ["matchId"]
            }
        }
    ],
}

reply_schema = {}
