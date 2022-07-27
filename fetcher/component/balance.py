"""collect data from exchange and store in database"""
import asyncio

from typing import Any

import redis
from fetcher.database import get_key, store_data
from fetcher.utils import safe_timeout_method, setup_logging

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt

logger = setup_logging(__name__)


def push_data(
    redis_client: redis.Redis,
    table: str,
    account_name: str,
    value: Any,
    expiry: float = 300,
) -> None:
    """store data in database"""
    key = get_key(table, account_name)
    logger.info("%s: %s", key, value)
    store_data(redis_client, key, value, expiry)


def parse_balance(balance: dict[str, Any]) -> dict[str, Any]:
    """parse balance"""
    return {
        "free": balance["free"],
        "used": balance["used"],
        "total": balance["total"],
        "timestamp": balance["timestamp"],
    }


async def start_balance_loop(
    clients: dict[str, ccxt.Exchange], redis_db: redis.Redis
) -> None:
    """collect data from exchange and store in database"""
    tasks = []
    for client in clients.values():
        if client.has.get("watchBalance"):
            tasks.append(asyncio.create_task(watch_balance_loop(client, redis_db)))
        else:
            tasks.append(asyncio.create_task(fetch_balance_loop(client, redis_db)))
    try:
        await asyncio.gather(*tasks)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("shutting down")
    finally:
        await asyncio.gather(*[client.close() for client in clients])


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
