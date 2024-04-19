riot_service_request_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["ACC_BY_RIOT_ID", "MATCHES_BY_RIOT_ID", "REFRESH_MATCHES_BY_RIOT_ID", "NEXT_20_MATCHES", "CHALL_ACCS", "ACC_BY_SUMM_ID", "MATCHES_BY_PUUID"]},
        "gameName": {"type": "string"},
        "tagLine": {"type": "string"},
        "summId": {"type": "string"},
        "puuid": {"type": "string"},
        "snapshotTimeThreshold": {"type": "string"},
        "matchStartIndex": {"type": "integer", "minimum": 0}
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
                    "action": {"const": "NEXT_20_MATCHES"}
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
        }
    ],
}

riot_service_reply_schema = {}