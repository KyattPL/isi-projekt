import asyncio
import datetime
from datetime import datetime as dt
from rabbit_client import RabbitMQClient


async def request_new_snapshot_data(rabbit_client):
    await rabbit_client.send_data_to_riot_service({"action": "NEW_SNAPSHOT_REQUEST"})


async def run_at(time, coro):
    now = dt.now()
    delay = ((time - now) % datetime.timedelta(days=1)).total_seconds()
    await asyncio.sleep(delay)
    return await coro


async def main():
    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop)

    # Schedule send_messages to run at a specific time every day
    time = dt.combine(datetime.date.today(), datetime.time(16, 47))
    while True:
        try:
            await run_at(time, request_new_snapshot_data(rabbit_client))
        except KeyboardInterrupt:
            print("Closing RabbitMQ client...")
            await rabbit_client.connection.close()
            loop.stop()
            loop.close()
            break

if __name__ == "__main__":
    asyncio.run(main())
