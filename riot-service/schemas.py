action_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["ACC_BY_RIOT_ID", "MATCHES_BY_RIOT_ID", "REFRESH_MATCHES_BY_RIOT_ID", "NEW_SNAPSHOT_DATA", "NEXT_20_MATCHES"]},
        "gameName": {"type": "string"},
        "tagLine": {"type": "string"},
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
                    "action": {"const": "NEW_SNAPSHOT_DATA"}
                }
            },
            "then": {
                "required": ["snapshotTimeThreshold"]
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
        }
    ],
}