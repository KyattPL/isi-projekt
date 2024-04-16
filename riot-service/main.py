import asyncio
import redis
from rabbit_client import RabbitMQClient

# Assuming RabbitMQClient is defined as shown in the previous example
#rabbit_client = RabbitMQClient(loop=asyncio.get_event_loop())

if __name__ == "__main__":
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop, r)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Closing RabbitMQ client...")
        loop.run_until_complete(rabbit_client.connection.close())
        loop.close()