import asyncio
import datetime
from datetime import datetime as dt
from rabbit_client import RabbitMQClient
from enum import Enum

class Action(Enum):
    ACC_BY_RIOT_ID = "ACC_BY_RIOT_ID"
    MATCHES_BY_RIOT_ID = "MATCHES_BY_RIOT_ID"
    REFRESH_MATCHES_BY_RIOT_ID = "REFRESH_MATCHES_BY_RIOT_ID"
    NEXT_20_MATCHES = "NEXT_20_MATCHES"
    CHALL_ACCS = "CHALL_ACCS"
    ACC_BY_SUMM_ID = "ACC_BY_SUMM_ID"
    MATCHES_BY_PUUID = "MATCHES_BY_PUUID"
    MATCHES_BY_PUUID_24HRS = "MATCHES_BY_PUUID_24HRS"
    MATCH_DATA_BY_MATCH_ID = "MATCH_DATA_BY_MATCH_ID"

async def send_data_to_service(rabbit_client, action, data=None):
    if data is None:
        data = {}
    return await rabbit_client.send_data_to_riot_service({"action": action.value, **data})

async def process_accounts(rabbit_client, accs):
    accs_puuids = []
    for acc in accs:
        resp = await send_data_to_service(rabbit_client, Action.ACC_BY_SUMM_ID, {"summId": acc['summonerId']})
        accs_puuids.append(resp['puuid'])
    return accs_puuids

async def fetch_match_ids(rabbit_client, accs_puuids, seconds_passed):
    match_ids = set()
    for puuid in accs_puuids:
        resp = await send_data_to_service(rabbit_client, Action.MATCHES_BY_PUUID_24HRS, {"puuid": puuid, "snapshotTimeThreshold": seconds_passed})
        for match in resp:
            match_ids.add(match)
    return match_ids

async def fetch_match_data(rabbit_client, match_ids):
    matches_data = []
    for match_id in match_ids:
        resp = await send_data_to_service(rabbit_client, Action.MATCH_DATA_BY_MATCH_ID, {"matchId": match_id})
        matches_data.append(resp)
    return matches_data

async def send_messages(rabbit_client):
    accs = await send_data_to_service(rabbit_client, Action.CHALL_ACCS)
    accs = accs[:90]

    accs_puuids = await process_accounts(rabbit_client, accs)

    await asyncio.sleep(120)

    start_date = dt.strptime('16/06/2021', '%d/%m/%Y')
    yesterday = dt.now() - datetime.timedelta(days=1)
    seconds_passed = int((yesterday - start_date).total_seconds())

    match_ids = await fetch_match_ids(rabbit_client, accs_puuids, seconds_passed)

    matches_data = await fetch_match_data(rabbit_client, match_ids)

    for m in matches_data:
        for p in m['info']['participants']:
            pass

    # print(matches_data[0])

    # with open('matches_data_sample.txt', 'w', encoding='utf-8') as file:
    #     for m in matches_data:
    #         file.write(f"{m}\n")

async def run_at(time, coro):
    now = dt.now()
    delay = ((time - now) % datetime.timedelta(days=1)).total_seconds()
    await asyncio.sleep(delay)
    return await coro

async def main():
    loop = asyncio.get_event_loop()
    rabbit_client = RabbitMQClient(loop)

    # Schedule send_messages to run at a specific time every day
    time = dt.combine(datetime.date.today(), datetime.time(16, 51))
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
