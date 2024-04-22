notification_service_request_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["SEND_PAYMENT_STATUS", "SEND_PREMIUM_CONFIRMATION"]},
        "userEmail": {"type": "string"},
        "userCredentials": {"type": "string"},
        "paymentStatus": {"type": "string"}
    },
    "required": ["action"],
    "anyOf": [
        {
            "if": {
                "properties": {
                    "action": {"const": "SEND_PAYMENT_STATUS"}
                }
            },
            "then": {
                "required": ["userEmail", "userCredentials", "paymentStatus"]
            }   
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "SEND_PREMIUM_CONFIRMATION"}
                }
            },
            "then": {
                "required": ["userEmail", "userCredentials"]
            }
        }
    ],
}

notification_service_reply_schema = {}