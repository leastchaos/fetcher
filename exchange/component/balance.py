"""collect data from exchange and store in database"""
import asyncio
from typing import Any

import redis

from exchange.utils import push_data, safe_timeout_method

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


def parse_balance(balance: dict[str, Any]) -> dict[str, Any]:
    """parse balance"""
    return {
        "free": balance["free"],
        "used": balance["used"],
        "total": balance["total"],
        "timestamp": balance["timestamp"],
    }


def start_balance_loop(
    clients: dict[str, ccxt.Exchange], redis_db: redis.Redis
) -> list[asyncio.Task]:
    """collect data from exchange and store in database"""
    tasks = []
    for client in clients.values():
        if client.has.get("watchBalance"):
            tasks.append(asyncio.create_task(watch_balance_loop(client, redis_db)))
        else:
            tasks.append(asyncio.create_task(fetch_balance_loop(client, redis_db)))
    return tasks


async def fetch_balance_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    while True:
        balance = await safe_timeout_method(client.fetch_balance)
        if balance:
            balance["timestamp"] = client.milliseconds()
            balance = parse_balance(balance)
            push_data(db, "balance", name, balance)
        await asyncio.sleep(1)


async def watch_balance_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    while True:
        balance = await safe_timeout_method(
            client.watch_balance, fail_func=client.fetch_balance
        )
        if balance:
            balance["timestamp"] = client.milliseconds()
            balance = parse_balance(balance)
            push_data(db, "balance", name, balance)
