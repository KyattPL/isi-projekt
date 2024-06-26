import requests
import jsonschema
import json
import webbrowser
import schemas
import asyncio
from aio_pika import connect_robust, Message

oauth_url = 'https://secure.snd.payu.com/pl/standard/user/oauth/authorize'
order_url = 'https://secure.snd.payu.com/api/v2_1/orders'


class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        self.token = "93de592d-935e-45ec-a0cd-564fc9469f52"
        self.loop.create_task(self.consume())

    async def connect_and_consume(self):
        # Nawiązywanie połączenia z RabbitMQ
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()  # Tworzenie kanału
        self.queue = await self.channel.declare_queue('payment.request', durable=False)
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

    async def send_data_to_queue(self, data, routing_key):
        data_bytes = json.dumps(data).encode()
        message = Message(body=data_bytes)
        await self.channel.default_exchange.publish(message, routing_key)
        print("Sent data to queue: " + routing_key)

    async def process_incoming_message(self, message):
        msg = message.body.decode()
        temp_shit = json.loads(msg)

        msg_json = {"action": "CREATE_ORDER", "customerIp": "127.0.0.1", "merchantPosId": "478129", "description": "CloneGG",
                    "currencyCode": "PLN", "totalAmount": "1", "products": [{"name": "Konto premium", "unitPrice": "1", "quantity": "1"}]}

        if not await self.validate_message(msg_json, schemas.payment_service_request_schema):
            return

        action = msg_json['action']

        # CO 12 H BEDZIE REFRESH
        if action == "CREATE_AUTH_TOKEN":
            self.token = self.create_oauth_token(msg_json)

        elif action == "CREATE_ORDER":
            if (self.token):
                authorization = 'Bearer ' + self.token
                msg_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'{authorization}'
                }
            else:
                msg_headers = message.headers
            await self.handle_order(msg_json, msg_headers, temp_shit['email'])

        await message.ack()

    # Tworzy oauth token potrzebny do stworzenia zamówienia
    def create_oauth_token(self, msg_json):
        try:
            oauth_response = requests.post(oauth_url, data=msg_json)
            oauth_token = oauth_response.json().get('access_token')
            print("Access token: " + oauth_token)

            return oauth_token

        except Exception as e:
            print(f"An error occurred while creating oauth token: {e}")

    # Tworzy zamówienie
    def create_order(self, msg_json, msg_headers):
        try:
            msg_json['continueUrl'] = 'http://localhost:3000/premium'
            msg_json['notifyUrl'] = 'http://localhost:8000/notify_premium_order'
            order_response = requests.post(
                order_url, json=msg_json, headers=msg_headers)
            print("Redirecting user to PayU payment page...")
            return order_response.url
            # webbrowser.open(order_response.url)
            # order_id = order_response.url.split('?orderId=')[1].split('&')[0]
            # return order_id

        except Exception as e:
            print(f"An error occurred while creating an order: {e}")
            return e

    # Sprawdza status zamówienia po Id
    def check_status_order(self, msg_headers, order_id):
        try:
            # Adding current orderId to url
            status_url = f"{order_url}/{order_id}"
            # Making the GET request
            status_response = requests.get(status_url, headers=msg_headers)
            # Getting status of the order
            status = status_response.json().get(
                'orders', [{}])[0].get('status')
            return status

        except Exception as e:
            print(f"An error occurred while checking status of an order: {e}")
            return e

    # Tworzy zamówienie, sprawdza jego status i wysyła powiadomienia
    async def handle_order(self, msg_json, msg_headers, email):
        order_status = 'NEW'
        processing_done = False

        try:
            # Stórz order i przekieruj na stronę
            order_url = self.create_order(msg_json, msg_headers)
            requests.post(
                f"http://localhost:8000/receive_payment_url/{email}", data=order_url)
            order_id = order_url.split('?orderId=')[1].split('&')[0]

            # Wyślij wiadomości w zależności od statusu zamówienia
            while (order_status != 'CANCELED' and order_status != 'COMPLETED'):
                order_status = self.check_status_order(msg_headers, order_id)
                print(order_status)
                # Wyślij wiadomość PENDING do notifications
                if (order_status == 'PENDING') and not processing_done:
                    await self.send_data_to_queue({"status": order_status, "email": email}, "notification.request")
                    processing_done = True
                    print(order_status)
                await asyncio.sleep(1)

            if (order_status == 'CANCELED'):
                # Wyślij wiadomość CANCELED do web i notifications
                await self.send_data_to_queue({"status": order_status, "email": email}, "payment.response.web")
                await self.send_data_to_queue({"action": "SEND_PAYMENT_STATUS", "userEmail": email, "paymentStatus": order_status}, "notification.request")
                print(order_status)
            elif (order_status == 'COMPLETED'):
                # Wyświj wiadomość COMPLETED do web i notifications
                await self.send_data_to_queue({"status": order_status, "email": email}, "payment.response.web")
                await self.send_data_to_queue({"action": "SEND_PAYMENT_STATUS", "userEmail": email, "paymentStatus": order_status}, "notification.request")
                print(order_status)

            return order_status

        except Exception as e:
            print(f"An error occurred while handling order: {e}")
            return e

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)
