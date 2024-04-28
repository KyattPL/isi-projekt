import json
import jsonschema
import schemas
import os.path
import base64
from aio_pika import connect_robust, Message
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import request_actions as RA
from request_actions import ActionType

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class RabbitMQClient:
    def __init__(self, loop):
        self.loop = loop
        self.connection = None
        self.channel = None
        self.queue = None
        self.loop.create_task(self.consume())
    

    async def connect_and_consume(self):
        self.connection = await connect_robust(host="localhost", port=5672, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("notifications.request", durable=False)
        await self.queue.consume(self.process_incoming_message, no_ack=False)
        return self.connection


    async def validate_message(self, action, schema):
        try:
            #message_data = json.loads(action)
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
        await self.channel.default_exchange.publish(message, routing_key="notifications.reply")


    def get_strategy(self, action):
        strategies = {
            ActionType.SEND_PAYMENT_STATUS: RA.SendPaymentStatus(),
            ActionType.SEND_PREMIUM_CONFIRMATION: RA.SendPremiumConfirmation(),
        }
        test = strategies.get(action, None)
        return test


    async def process_incoming_message(self, message):
        msg = message.body.decode()
        msg_json = json.loads(msg)
        
        if not await self.validate_message(msg_json, schemas.notification_service_request_schema):
            return

        action = ActionType(msg_json['action'])
        strategy = self.get_strategy(action)

        if strategy is None:
            print(f"No strategy found for action: {action.value}")
            await message.reject()
            return

        await strategy.execute(msg_json)
            
        await message.ack()


    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)