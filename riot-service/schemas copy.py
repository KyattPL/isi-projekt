action_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["ACC_BY_RIOT_ID", "CHALL_ACCS", "MATCH_BY_ID", "MATCH_BY_PUUID"]},
        "gameName": {"type": "string"},
        "tagLine": {"type": "string"},
        "puuid": {"type": "string"},
        "matchId": {"type": "string"}
    },
    "required": ["action"],
    "anyOf": [
        {
            "if": {
                "properties": {
                    "action": {"const": "ACC_BY_RIOT_ID"}
                }
            },
            "then": {
                "required": ["gameName", "tagLine"]
            }   
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "MATCH_BY_ID"}
                }
            },
            "then": {
                "required": ["matchId"]
            }   
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "MATCH_BY_PUUID"}
                }
            },
            "then": {
                "required": ["puuid"]
            }   
        }
    ],
}