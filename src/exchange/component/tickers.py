"""fetch tickers"""
import asyncio

import ccxt.async_support as ccxt
import redis

from src.exchange.utils import push_data, safe_timeout_method


async def fetch_tickers_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """fetch loans"""
    name = client.options["name"]
    while True:
        data = await safe_timeout_method(client.fetch_tickers)
        timestamp = client.milliseconds()
        for key, value in data.items():
            value["timestamp"] = timestamp
        if data:
            push_data(db, "tickers", name, data)
        await asyncio.sleep(60)


def start_tickers_loop(
    clients: dict[str, ccxt.Exchange], db: redis.Redis
) -> list[asyncio.Task]:
    """start loans loop"""
    return [
        asyncio.create_task(fetch_tickers_loop(client, db))
        for client in clients.values()
    ]
