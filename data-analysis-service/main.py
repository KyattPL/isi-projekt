import asyncio
import datetime
from datetime import datetime as dt
from rabbit_client import RabbitMQClient

async def send_messages(rabbit_client):
    #print("Sending initial data to Riot service")
    data = {"action": "CHALL_ACCS"}
    accs = await rabbit_client.send_data_to_riot_service(data)
    accs = accs[:90]

    accs_puuids = []
    for acc in accs:
        #print(f"Processing account: {acc['summonerId']}")
        resp = await rabbit_client.send_data_to_riot_service({"action": "ACC_BY_SUMM_ID", "summId": acc['summonerId']})
        accs_puuids.append(resp['puuid'])

    await asyncio.sleep(120)

    start_date = dt.strptime('16/06/2021', '%d/%m/%Y')
    yesterday = dt.now() - datetime.timedelta(days=1)
    seconds_passed = int((yesterday - start_date).total_seconds())

    match_ids = set()
    for puuid in accs_puuids:
        resp = await rabbit_client.send_data_to_riot_service({"action": "MATCHES_BY_PUUID", "puuid": puuid, "snapshotTimeThreshold": seconds_passed})
        for match in resp:
            match_ids.add(match)

    no_cycles = (len(match_ids) // 100) + 1
    print(no_cycles)

    matches_data = []
    match_ids_list = list(match_ids)
    index = 0
    while no_cycles > index:
        await asyncio.sleep(120)
        if (index+1)*100 > len(match_ids_list):
            for match_id in match_ids_list[index*100:]:
                resp = await rabbit_client.send_data_to_riot_service({"action": "MATCH_DATA_BY_MATCH_ID", "matchId": match_id})
                matches_data.append(resp)
        else:
            for match_id in match_ids_list[index*100:(index+1)*100]:
                resp = await rabbit_client.send_data_to_riot_service({"action": "MATCH_DATA_BY_MATCH_ID", "matchId": match_id})
                matches_data.append(resp)
        index += 1

    print(matches_data)
    with open('matches_data_sample.txt', 'w') as file:
        for m in matches_data:
            file.write(f"{m}\n")

async def run_at(time, coro):
    now = dt.now()
    delay = ((time - now) % datetime.timedelta(days=1)).total_seconds()
    await asyncio.sleep(delay)
    return await coro

async def main():
    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop)

    # Schedule send_messages to run at a specific time every day
    time = dt.combine(datetime.date.today(), datetime.time(1, 27))
    while True:
        try:
            await run_at(time, send_messages(rabbit_client))
        except KeyboardInterrupt:
            print("Closing RabbitMQ client...")
            await rabbit_client.connection.close()
            loop.stop()
            loop.close()
            break

if __name__ == "__main__":
    asyncio.run(main())