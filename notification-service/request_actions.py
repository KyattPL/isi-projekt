import json
import jsonschema
import schemas
import os.path
import base64
from enum import Enum
from aio_pika import connect_robust, Message
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import database as db

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class ActionType(Enum):
    SEND_PAYMENT_STATUS = "SEND_PAYMENT_STATUS"
    SEND_PREMIUM_CONFIRMATION = "SEND_PREMIUM_CONFIRMATION"
    SEND_NEW_USER_GREETINGS = "SEND_NEW_USER_GREETINGS"


class ActionStrategy:
    async def execute(self, msg_json):
        pass


class SendPaymentStatus(ActionStrategy):
    async def execute(self, msg_json):
        params = [msg_json['userEmail'], msg_json['paymentStatus']]
        receiverMail = params[0]
        mailBody = F"Hello, the status of your payment is as follows: {params[1]}."
        mailSubject = "Payment status"
        await sendMail(receiverMail, mailBody, mailSubject, userCredentials="None")


class SendPremiumConfirmation(ActionStrategy):
    async def execute(self, msg_json):
        params = [msg_json['userEmail']]
        receiverMail = params[0]
        mailBody = F"Hello, the payment process has been completed and you have received the premium membership."
        mailSubject = "Premium membership confirmation"
        await sendMail(receiverMail, mailBody, mailSubject, userCredentials="None")


class SendNewUserGreetings(ActionStrategy):
    async def execute(self, msg_json):
        params = [msg_json['userEmail'], msg_json['userCredentials']]
        receiverMail = params[0]
        userCredentials = params[1]
        mailBody = F"Welcome to our application {userCredentials}! We're excited to have you onboard!"
        mailSubject = "Welcome to Clone.gg"
        await sendMail(receiverMail, mailBody, mailSubject, userCredentials)


async def insert_notification_into_db(userEmail, userCredentials, messageSubject, messageBody):

    db.create_notifications_table()

    print(userEmail, userCredentials, messageSubject, messageBody)

    db.insert_notification(userEmail, userCredentials,
                           messageSubject, messageBody)


async def sendMail(receiverMail, mailBody, mailSubject, userCredentials):
    creds = None
    # Construct the path to the credentials.json file
    credentials_path = os.path.join(
        os.path.dirname(__file__), "credentials.json")
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
        raw_message = base64.urlsafe_b64encode(
            mailMessage.as_bytes()).decode("utf-8")

        # Send the message
        send_message = service.users().messages().send(
            userId="me", body={"raw": raw_message}).execute()
        print(F"Message Id: {send_message['id']}")
        await insert_notification_into_db(receiverMail, userCredentials, mailSubject, mailBody)
    except HttpError as error:
        print(f"An error occurred: {error}")
