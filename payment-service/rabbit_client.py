import requests
import jsonschema
import json
import webbrowser
import schemas
from aio_pika import connect_robust, Message

oauth_url = 'https://secure.snd.payu.com/pl/standard/user/oauth/authorize'
order_url = 'https://secure.snd.payu.com/api/v2_1/orders'

TOKEN = "XD"

class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        self.loop.create_task(self.consume())

    async def connect_and_consume(self):
        # Nawiązywanie połączenia z RabbitMQ
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()  # Tworzenie kanału
        self.queue = await self.channel.declare_queue('payments.request', durable=False)
        await self.queue.consume(self.process_incoming_message, no_ack=False)
        return self.connection
    
    async def validate_message(self, action, schema):
        try:
            jsonschema.validate(instance=action, schema=schema)
            print("Message is valid.")
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Message is invalid: {e}")
            return False
        except json.JSONDecodeError:
            print("Message is not a valid JSON.")
            return False
        
    async def send_data_to_queue(self, data):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)
        await self.channel.default_exchange.publish(message, routing_key="payments.reply")

    async def process_incoming_message(self, message):
        msg = message.body.decode()
        msg_json = json.loads(msg)
        
        if not await self.validate_message(msg_json, schemas.payment_service_request_schema):
            return
        
        action = msg_json['action']

        # CO 12 H BEDZIE REFRESH
        if action == "CREATE_AUTH_TOKEN":
            TOKEN = self.create_oauth_token(msg_json)

        elif action == "CREATE_ORDER":
            msg_headers = message.headers
            self.create_order(msg_json, msg_headers)
            
        await message.ack()

    def create_oauth_token(self, msg_json):
        try:
            oauth_response = requests.post(oauth_url, data=msg_json)
            print("Access token: " + oauth_response.json().get('access_token'))
            
            return oauth_response
        
        except Exception as e:
            print(f"An error occurred: {e}")

    # Tworzy order -> Stronka ------> To po Id odpytuj co 2 s Retrieve an order 
    # ------> Jeśli completed to wysyłam do notifications.request (michał) i payment.response.web (serwis web)
    def create_order(self, msg_json, msg_headers):
        try:
            order_response = requests.post(order_url, json=msg_json, headers=msg_headers)
            print("Redirecting user to PayU payment page...")
            webbrowser.open(order_response.url)

        except Exception as e:
            print(f"An error occurred: {e}")

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)

