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


    # async def send_data_to_riot_service(self, data):
    #     data_bytes = json.dumps(data).encode()
    #     message = Message(body=data_bytes)

    #     if not await self.validate_message(data, schemas.riot_service_request_schema):
    #         return

    #     await self.channel.default_exchange.publish(message, routing_key="lol.data.request")


    async def process_incoming_message(self, message):
        
        msg = message.body.decode()
        msg_json = json.loads(msg)
        
        if not await self.validate_message(msg_json, schemas.notification_service_request_schema):
            return
        
        action = msg_json['action']

        if action == "SEND_PAYMENT_STATUS":
            params = [msg_json['userEmail'], msg_json['userCredentials'], msg_json['paymentStatus']]
            receiverMail = params[0]
            mailBody = F"Hello {params[1]}, the status of your payment is as follows: {params[2]}."
            mailSubject = "Payment status"
            self.sendMail(receiverMail, mailBody, mailSubject)

        elif action == "SEND_PREMIUM_CONFIRMATION":
            params = [msg_json['userEmail'], msg_json['userCredentials']]
            receiverMail = params[0]
            mailBody = F"Hello {params[1]}, the payment process has been completed and you have received the premium membership."
            mailSubject = "Premium membership confirmation"
            self.sendMail(receiverMail, mailBody, mailSubject)
            
        await message.ack()

    def sendMail(self, receiverMail, mailBody, mailSubject):
        creds = None
        # Construct the path to the credentials.json file
        credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        # Construct the path to the token.json file
        token_path = os.path.join(os.path.dirname(__file__), "token.json")

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=creds)
            # Create a MIME message
            mailMessage = MIMEText(mailBody)
            mailMessage["to"] = receiverMail
            mailMessage["from"] = "riotserviceapp@gmail.com"
            mailMessage["subject"] = mailSubject

            # Encode the message
            raw_message = base64.urlsafe_b64encode(mailMessage.as_bytes()).decode("utf-8")
            #print(F"Message: {raw_message}")

            # Send the message
            send_message = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
            print(F"Message Id: {send_message['id']}")
        except HttpError as error:
            print(f"An error occurred: {error}")

    async def consume(self):
        await self.connect_and_consume()
        await self.queue.consume(self.process_incoming_message, no_ack=False)