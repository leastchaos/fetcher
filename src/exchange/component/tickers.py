"""fetch tickers"""
import asyncio
import logging

import ccxt.async_support as ccxt
import redis

from src.exchange.utils import push_data, safe_timeout_method


async def fetch_tickers_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """fetch loans"""
    name = client.options["name"]
    log_str = f"{name} fetch tickers"
    logging.info(f"fetching tickers for {name}")
    while True:
        data = await safe_timeout_method(client.fetch_tickers, log_str=log_str)
        timestamp = client.milliseconds()
        if not data:
            await asyncio.sleep(60)
            continue
        for key, value in data.items():
            value["timestamp"] = timestamp
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
