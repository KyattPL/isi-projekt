action_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["ACC_BY_RIOT_ID", "MATCHES_BY_RIOT_ID", "NEW_SNAPSHOT_DATA"]},
        "gameName": {"type": "string"},
        "tagLine": {"type": "string"},
        "snapshotTimeThreshold": {"type": "string"},
    },
    "required": ["action"],
    "anyOf": [
        {
            "if": {
                "properties": {
                    "action": {"enum": ["ACC_BY_RIOT_ID", "MATCHES_BY_RIOT_ID"]}
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
        }
    ],
}