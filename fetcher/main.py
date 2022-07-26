"""collect data from exchange and store in database"""
import asyncio
import logging
from typing import Any, Awaitable, Callable

import async_timeout

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


balances: dict[str, dict[str, Any]] = {}


async def store_data(table: str, key: str, value: Any) -> None:
    """store data in database"""
    print(f"{table} {key} {value}")


async def start_balance_loop(clients: dict[str, ccxt.Exchange]) -> None:
    """collect data from exchange and store in database"""
    tasks = []
    for client in clients.values():
        if client.has.get("watchBalance"):
            tasks.append(asyncio.create_task(watch_balance_loop(client)))
        else:
            tasks.append(asyncio.create_task(fetch_balance_loop(client)))
    try:
        await asyncio.gather(*tasks)
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
        return await func(*args)
    except (ccxt.errors.NetworkError, asyncio.TimeoutError) as err:
        logging.error("%s(%s) failed: %s", func.__name__, args, err)
    if not fail_func:
        return fail_result
    return await safe_timeout_method(
        fail_func, *args, fail_result=fail_result, timeout=fail_timeout
    )


async def fetch_balance_loop(client: ccxt.Exchange) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    while True:
        balances[name] = await safe_timeout_method(
            client.fetch_balance, fail_result=balances.get(name, {})
        )
        balances[name]["timestamp"] = client.milliseconds()
        await store_data("balance", name, balances[name])
        await asyncio.sleep(1)


async def watch_balance_loop(client: ccxt.Exchange) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    while True:
        balances[name] = await safe_timeout_method(
            client.watch_balance,
            fail_func=client.fetch_balance,
            fail_result=balances.get(name, {}),
        )
        await store_data("balance", name, balances[name])


async def shutdown(clients: dict[str, ccxt.Exchange]) -> None:
    """shutdown exchange"""
    for client in clients.values():
        await client.close()


if __name__ == "__main__":
    from fetcher.client import get_clients

    logging.basicConfig(level=logging.INFO)
    clients = get_clients()
    asyncio.run(start_balance_loop(clients))
