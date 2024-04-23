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


async def get_rabbit_client():
    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop)
    await rabbit_client.connect_and_consume()
    yield rabbit_client
    if rabbit_client.connection is not None:
        await rabbit_client.connection.close()


@app.on_event("shutdown")
async def shutdown_event(rabbit_client: RabbitMQClient = Depends(get_rabbit_client)):
    await rabbit_client.connection.close()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/some_endpoint")
async def some_endpoint(rabbit_client: RabbitMQClient = Depends(get_rabbit_client)):
    # Use rabbit_client here
    return {"message": "This is an example endpoint"}


@app.get("/matches_by_riot_id/{gameName}/{tagLine}")
async def some_endpoint(gameName, tagLine, rabbit_client: RabbitMQClient = Depends(get_rabbit_client)):
    resp = await rabbit_client.send_data_to_riot_service({"action": "MATCHES_BY_RIOT_ID", "gameName": gameName, "tagLine": tagLine})
    return resp
