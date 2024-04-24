import asyncio
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rabbit_client import RabbitMQClient


app = FastAPI()

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


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/some_endpoint")
async def some_endpoint(rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    # Use rabbit_client here
    return {"message": "This is an example endpoint"}


@app.get("/matches_data_by_riot_id/{gameName}/{tagLine}")
async def some_endpoint(gameName, tagLine, rabbit_client_instance: RabbitMQClient = Depends(get_rabbit_client)):
    matches = await rabbit_client_instance.send_data_to_riot_service({"action": "MATCHES_BY_RIOT_ID", "gameName": gameName, "tagLine": tagLine})

    matches_data = []
    for match in matches:
        resp = await rabbit_client_instance.send_data_to_riot_service({"action": "MATCH_DATA_BY_MATCH_ID", "matchId": match})
        matches_data.append(resp)

    return matches_data
