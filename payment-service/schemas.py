payment_service_request_schema = {
    "type": "object",
    "properties": {
        "action": {"enum": ["CREATE_AUTH_TOKEN", "CREATE_ORDER"]},
        "grant_type": {"type": "string"},
        "client_id": {"type": "string"},
        "client_secret": {"type": "string"},
        "customerIp": {"type": "string"},
        "merchantPosId": {"type": "string"},
        "description": {"type": "string"},
        "currencyCode": {"type": "string"},
        "totalAmount": {"type": "string"},
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": { "type": "string" },
                    "unitPrice": { "type": "string" },
                    "quantity": { "type": "string" }
                },
                "required": ["name", "unitPrice", "quantity"]
            }
        }
    },
    "required": ["action"],
    "anyOf": [
        {
            "if": {
                "properties": {
                    "action": {"const": "CREATE_AUTH_TOKEN"}
                }
            },
            "then": {
                "required": ["grant_type", "client_id", "client_secret"]
            }   
        },
        {
            "if": {
                "properties": {
                    "action": {"const": "CREATE_ORDER"}
                }
            },
            "then": {
                "required": ["customerIp", "merchantPosId", "description", "currencyCode", "totalAmount", "products"]
            }
        }
    ],
    "headers": {
        "type": "object",
        "properties": {
            "Authorization": { "type": "string" },
            "Content-Type": { "const": "application/json" }
            },
            "required": ["Authorization", "Content-Type"]
        }
}