import asyncio
from fastapi import Depends, FastAPI
from rabbit_client import RabbitMQClient


app = FastAPI()


async def get_rabbit_client():
    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop)
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
