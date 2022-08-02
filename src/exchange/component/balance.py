"""collect data from exchange and store in database"""
import asyncio
import logging
from typing import Any

import redis

from src.exchange.utils import push_data, safe_timeout_method

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


def parse_balance(balance: dict[str, Any]) -> dict[str, Any]:
    """parse balance"""
    assets_to_delete = [
        asset for asset, value in balance["total"].items() if value == 0
    ]
    for asset in assets_to_delete:
        del balance["total"][asset]
        del balance["free"][asset]
        del balance["used"][asset]
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
        if client.id == "gateio" and client.options["defaultMarginMode"] == "isolated":
            tasks.append(
                asyncio.create_task(
                    fetch_gateio_isolated_balance_loop(client, redis_db)
                )
            )
        elif client.has.get("watchBalance"):
            tasks.append(asyncio.create_task(watch_balance_loop(client, redis_db)))
        else:
            tasks.append(asyncio.create_task(fetch_balance_loop(client, redis_db)))
    return tasks


async def fetch_gateio_isolated_balance_loop(
    client: ccxt.Exchange, db: redis.Redis
) -> None:
    """
    collect data from exchange and store in database
    TODO: refactor this in general loop
    """
    name = client.options["name"]
    log_str = f"{name} fetch balance"
    logging.info(f"fetching balance for {name}")
    while True:
        balances = await safe_timeout_method(
            client.fetch_balance, log_str=log_str, fail_result={}
        )
        balances.pop("info", None)
        for market, balance in balances.items():
            market_name = f"{name}-{market}"
            balance["timestamp"] = client.milliseconds()
            balance = parse_balance(balance)
            push_data(db, "balance", market_name, balance)
        await asyncio.sleep(60)


async def fetch_balance_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} fetch balance"
    logging.info(f"fetching balance for {name}")
    while True:
        balance = await safe_timeout_method(client.fetch_balance, log_str=log_str)
        if balance:
            balance["timestamp"] = client.milliseconds()
            balance = parse_balance(balance)
            push_data(db, "balance", name, balance)
        await asyncio.sleep(1)


async def watch_balance_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} watch balance"
    logging.info(f"watching balance for {name}")
    err_count = 0
    try:
        balance = await client.fetch_balance()
    except Exception as e:
        logging.error("%s failed to fetch balance retrying: %s", name, e)
        await asyncio.sleep(1)
        return await watch_balance_loop(client, db)
    while True:
        update = await safe_timeout_method(
            client.watch_balance, fail_func=client.fetch_balance, log_str=log_str
        )
        if not update:
            err_count += 1
            if err_count > 10:
                logging.error(f"{name} balance watch failed")
                balance = await safe_timeout_method(
                    client.fetch_balance, fail_result=balance, log_str=log_str
                )
                await client.close()
                err_count = 0
            push_balance = parse_balance(balance)
            push_data(db, "balance", name, push_balance)
            await asyncio.sleep(1)
            continue
        balance = client.deep_extend(balance, update)
        balance["timestamp"] = client.milliseconds()
        push_balance = parse_balance(balance)
        push_data(db, "balance", name, push_balance)
        err_count = 0
