import os.path
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main():
  creds = None

  # Construct the path to the credentials.json file
  credentials_path = os.path.join(os.path.dirname(__file__), "test", "credentials.json")

  # Construct the path to the token.json file
  token_path = os.path.join("test", "token.json")

  # Check if the folder exists, if not, create it
  if not os.path.exists("test"):
      os.makedirs("test")

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
    message = MIMEText("This is the body of the email.")
    message["to"] = "aniomio2000@wp.pl"
    message["from"] = "riotserviceapp@gmail.com"
    message["subject"] = "Hello from Python"

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    #print(F"Message: {raw_message}")

    # Send the message
    send_message = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
    print(F"Message Id: {send_message['id']}")

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()