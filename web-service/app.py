import asyncio
from datetime import timedelta, datetime
import json
import os
import time
from fastapi import Depends, FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel
import requests
from rabbit_client import RabbitMQClient
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session

import database as db

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
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
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

app.add_middleware(GZipMiddleware, minimum_size=1000)

rabbit_client_instance = None
sessions = {}
SESSION_EXPIRATION_TIME = timedelta(minutes=30)


def cleanup_expired_sessions():
    while True:
        current_time = datetime.now()
        for email, session_data in list(sessions.items()):
            if current_time - session_data['last_activity'] > SESSION_EXPIRATION_TIME:
                del sessions[email]
        time.sleep(60)  # Check every 60 seconds


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

    cleanup_expired_sessions_task = BackgroundTasks()
    cleanup_expired_sessions_task.add_task(cleanup_expired_sessions)

    if rabbit_client_instance is None:
        rabbit_client_instance = await get_rabbit_client()


@app.on_event("shutdown")
async def shutdown_event():
    global rabbit_client_instance
    if rabbit_client_instance is not None:
        await rabbit_client_instance.connection.close()


@app.get("/auth/google/login")
async def google_auth_redirect():
    print(authentication_url, flush=True)
    return {"message": authentication_url}


@app.get("/auth/google/callback")
async def google_auth_callback(request: Request, rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    extracted_code = request.query_params.get('code')
    if not extracted_code:
        raise HTTPException(status_code=400, detail="Code not found")

    data = client.prepare_request_body(
        code=extracted_code,
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True
    )

    token_url = 'https://oauth2.googleapis.com/token'
    response = requests.post(token_url, params=data)

    client.parse_request_body_response(response.text)

    credentials = Credentials(client.token['access_token'])

    service = build('people', 'v1', credentials=credentials)
    results = service.people().get(resourceName='people/me',
                                   personFields='names,emailAddresses').execute()

    if not results:
        print("No name nor mail found.")
    else:
        name = results['names'][0]['displayName']
        email = results['emailAddresses'][0]['value']

        sessions[email] = {"name": name, "email": email,
                           "last_activity": datetime.now()}

        userObj = db.get_user_from_db(email)

        if userObj is None:
            db.insert_user_into_db(email, name)
            hasPremium = False
            print(f"________________________________________________\n")
            print(f"email: {email}\n")
            print(f"name: {name}\n")
            print(f"hasPremium: {userObj}\n")
            print(f"________________________________________________\n")
            await rabbit_client_instance.send_data_to_notification_service(
                {"action": "SEND_NEW_USER_GREETINGS", "userEmail": email, "userCredentials": name})

        if userObj != None and userObj[3] == 0:
            hasPremium = False
        else:
            hasPremium = True

        html_content = f"""
        <html>
        <body>
            <script>
                window.opener.postMessage({{ "email": "{email}", "status": "OK", "hasPremium": "{hasPremium}"}}, "*");
                window.close();
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    # google drive files request:
    # drive = build('drive', 'v2', credentials=credentials)
    # files = drive.files().list().execute()
    # items = files.get('files', [])
    # if not items:
    #     print("No files found.")
    # else:
    #     for item in items:
    #         print(f"File Name: {item['name']}, File ID: {item['id']}")


@app.delete("/session/{email}")
async def remove_user_from_session(email: str):
    if email in sessions:
        del sessions[email]
        return {"message": f"User {email} removed from session."}
    else:
        raise HTTPException(
            status_code=404, detail="User not found in session.")


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


@app.get("/buy_premium/{email}")
async def buy_premium(email, rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    print(email)
    await rabbit_client_instance.send_data_to_payment_service({"action": "CREATE_ORDER", "email": email})
    return


@app.post("/receive_payment_url/{email}")
async def receive_payment_url(request: Request, email):
    resp = await request.body()
    decoded = resp.decode("utf-8")
    sessions[email]['paymentUrl'] = decoded
    return


@app.get("/get_payment_url/{email}")
async def get_payment_url(email):
    if 'paymentUrl' in sessions[email].keys():
        return sessions[email]['paymentUrl']
    else:
        return "NO_URL"


@app.post("/notify_premium_order")
async def notify_premium_order(request: Request):
    body = await request.body()
    print(body)
    return Response(status_code=200)


@app.get("/is_user_premium/{email}")
async def is_user_premium(email):
    return db.user_has_premium(email)


@app.get("/get_snapshot_for_champ/{champ}")
async def get_snapshot_for_champ(champ):
    return db.get_champ_from_snapshot(champ)


@app.middleware("http")
async def update_last_activity(request: Request, call_next):
    response = await call_next(request)
    email = request.headers.get("X-User-Email")
    if email and email in sessions:
        sessions[email]['last_activity'] = datetime.now()
    return response
