action_schema = {
    "type": "object",
    "properties": {
        "action": {"type": "string"},
        "gameName": {"type": "string"},
        "tagLine": {"type": "string"}
    },
    "required": ["action"],
    "if": {
        "properties": {
            "action": {"const": "ACC_BY_RIOT_ID"}
        }
    },
    "then": {
        "required": ["gameName", "tagLine"]
    }
}