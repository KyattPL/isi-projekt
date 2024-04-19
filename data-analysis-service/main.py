import asyncio
from rabbit_client import RabbitMQClient

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop)
    try:
        #loop.run_until_complete(rabbit_client.connect_and_consume())
        loop.run_until_complete(rabbit_client.send_data_to_riot_service({"action": "ACC_BY_RIOT_ID", "gameName": "KyattPL", "tagLine": "EUW"}))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Closing RabbitMQ client...")
        loop.run_until_complete(rabbit_client.connection.close())
        loop.close()