"""collect data from exchange and store in database"""
import asyncio

from typing import Any, Awaitable, Callable

import async_timeout
import redis
from fetcher.client import get_clients
from fetcher.database import get_redis, get_key, store_data
from fetcher.utils import setup_logging

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt

logger = setup_logging(__name__)
balances: dict[str, dict[str, Any]] = {}


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
        await shutdown(clients)


async def safe_timeout_method(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    timeout: float = 10,
    fail_func: Callable[..., Awaitable[Any]] | None = None,
    fail_result: Any = None,
    fail_timeout: float = 10,
) -> Any:
    """try calling the method, if failed return fail result"""
    try:
        async with async_timeout.timeout(timeout):
            return await func(*args)
    except (ccxt.errors.NetworkError, asyncio.TimeoutError) as err:
        logger.error("%s(%s) failed: %s", func.__name__, args, err)
    if not fail_func:
        return fail_result
    return await safe_timeout_method(
        fail_func, *args, fail_result=fail_result, timeout=fail_timeout
    )


async def fetch_balance_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    while True:
        balance = await safe_timeout_method(client.fetch_balance)
        if balance:
            balances[name] = balance
            balances[name]["timestamp"] = client.milliseconds()
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
            balances[name] = balance
            balances[name]["timestamp"] = client.milliseconds()
            balance = parse_balance(balance)
            push_data(db, "balance", name, balance)


async def shutdown(clients: dict[str, ccxt.Exchange]) -> None:
    """shutdown exchange"""
    for client in clients.values():
        await client.close()


if __name__ == "__main__":
    exchanges = get_clients()
    database = get_redis()
    asyncio.run(start_balance_loop(exchanges, database))
