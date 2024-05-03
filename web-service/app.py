import asyncio
import json
import os
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel
import requests
from rabbit_client import RabbitMQClient
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session

app = FastAPI()

# Google OAuth2 configuration
CLIENT_ID = "1004980276527-a99su492ckbo05dfji1i555dvt3v6jkc.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"
SCOPE = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/contacts.readonly",
    "profile",
    "https://www.googleapis.com/auth/userinfo.email"
]


client = WebApplicationClient(CLIENT_ID)
authentication_url = client.prepare_request_uri(
  'https://accounts.google.com/o/oauth2/auth',
  redirect_uri = REDIRECT_URI,
  scope = SCOPE,
)


origins = [
    "http://localhost:3000",
    "localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


rabbit_client_instance = None


async def get_rabbit_client():
    global rabbit_client_instance
    if rabbit_client_instance is None:
        loop = asyncio.get_event_loop()
        rabbit_client_instance = RabbitMQClient(loop)
        await rabbit_client_instance.connect_and_consume()
    return rabbit_client_instance


@app.on_event("startup")
async def startup_event():
    global rabbit_client_instance
    if rabbit_client_instance is None:
        rabbit_client_instance = await get_rabbit_client()


@app.on_event("shutdown")
async def shutdown_event():
    global rabbit_client_instance
    if rabbit_client_instance is not None:
        await rabbit_client_instance.connection.close()


# FastAPI endpoints
@app.get("/auth/google/login")
async def google_auth_redirect():
    print(authentication_url, flush=True)
    return {"url": authentication_url}


@app.get("/auth/google/callback")
async def google_auth_callback(request: Request):
    extracted_code = request.query_params.get('code')
    if not extracted_code:
        raise HTTPException(status_code=400, detail="Code not found")

    data = client.prepare_request_body(
        code = extracted_code,
        redirect_uri = REDIRECT_URI,
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        include_client_id=True
    )

    token_url = 'https://oauth2.googleapis.com/token'
    response = requests.post(token_url, params=data)

    client.parse_request_body_response(response.text)

    credentials = Credentials(client.token['access_token'])

    service = build('people', 'v1', credentials=credentials)
    results = service.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()
    print(f"Name: {results['names'][0]['displayName']}")
    print(f"Email: {results['emailAddresses'][0]['value']}")

    # google drive files request:
    # drive = build('drive', 'v2', credentials=credentials)
    # files = drive.files().list().execute()
    # items = files.get('files', [])
    # if not items:
    #     print("No files found.")
    # else:
    #     for item in items:
    #         print(f"File Name: {item['name']}, File ID: {item['id']}")
    


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/matches_data_by_riot_id/{gameName}/{tagLine}")
async def matches_data_by_riot_id(gameName, tagLine, rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    matches = await rabbit_client_instance.send_data_to_riot_service({"action": "MATCHES_BY_RIOT_ID", "gameName": gameName, "tagLine": tagLine})

    matches_data = []
    for match in matches:
        resp = await rabbit_client_instance.send_data_to_riot_service({"action": "MATCH_DATA_BY_MATCH_ID", "matchId": match})
        matches_data.append(resp)

    return matches_data


@app.get("/refresh_matches_data_by_riot_id/{gameName}/{tagLine}")
async def refresh_matches_data_by_riot_id(gameName, tagLine, rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    matches = await rabbit_client_instance.send_data_to_riot_service({"action": "REFRESH_MATCHES_BY_RIOT_ID", "gameName": gameName, "tagLine": tagLine})

    matches_data = []
    for match in matches:
        resp = await rabbit_client_instance.send_data_to_riot_service({"action": "MATCH_DATA_BY_MATCH_ID", "matchId": match})
        matches_data.append(resp)

    return matches_data


@app.get("/next10_matches_data_by_riot_id/{gameName}/{tagLine}/{startIndex}")
async def next10_matches_data_by_riot_id(gameName, tagLine, startIndex, rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    matches = await rabbit_client_instance.send_data_to_riot_service({"action": "NEXT_10_MATCHES", "gameName": gameName, "tagLine": tagLine, "matchStartIndex": int(startIndex)})
    print(matches)

    matches_data = []
    for match in matches:
        resp = await rabbit_client_instance.send_data_to_riot_service({"action": "MATCH_DATA_BY_MATCH_ID", "matchId": match})
        matches_data.append(resp)

    return matches_data
