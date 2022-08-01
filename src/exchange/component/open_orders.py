"""collect open order data from exchange and store in database"""
import asyncio
import logging
from typing import Any

import redis

from src.exchange.component.client import get_clients
from src.exchange.models.orders import Order, OrderDict
from src.exchange.utils import push_data, safe_timeout_method

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


OrderSymbolCache = dict[str, dict[str, OrderDict]]
OrderCache = dict[str, OrderSymbolCache]


def parse_open_order(open_order: dict[str, Any]) -> OrderDict:
    """parse open orders"""
    try:
        return Order.parse_obj(open_order).dict()
    except Exception as err:
        logging.error("%s error: %s", open_order, err)
        return {}


def start_open_orders_loop(
    clients: dict[str, ccxt.Exchange], redis_db: redis.Redis
) -> list[asyncio.Task]:
    """collect data from exchange and store in database"""
    tasks = []
    for client in clients.values():
        if client.id == "gateio":
            tasks.append(
                asyncio.create_task(watch_gateio_open_orders_loop(client, redis_db))
            )
        elif client.has.get("watchOrders"):
            tasks.append(asyncio.create_task(watch_open_orders_loop(client, redis_db)))
        else:
            tasks.append(asyncio.create_task(fetch_open_orders_loop(client, redis_db)))
    return tasks


async def fetch_open_orders_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} fetch open orders"
    logging.info(f"fetching open orders for {name}")
    while True:
        data = await safe_timeout_method(client.fetch_open_orders, log_str=log_str)
        if data:
            data = {
                order["symbol"]: {order["id"]: parse_open_order(order)}
                for order in data
            }
            push_data(db, "open_orders", name, data)
        await asyncio.sleep(1)


def update_orders(orders: OrderCache, update: list[OrderDict]) -> OrderCache:
    """update orders"""
    for order in update:
        if order["symbol"][-5:] == "USDTM":
            continue
        if order["symbol"] not in orders:
            orders[order["symbol"]] = {}
        if order["status"] == "open":
            orders[order["symbol"]][order["id"]] = parse_open_order(order)
        else:
            orders[order["symbol"]].pop(order["id"], None)
    return orders


async def fetch_open_orders(
    client: ccxt.Exchange, default: OrderCache = None
) -> OrderCache:
    """fetch open orders"""
    try:
        data = await client.fetch_open_orders()
    except Exception as err:
        logging.error("%s error: %s", client.options["name"], err)
        return default
    data = {order["symbol"]: {order["id"]: parse_open_order(order)} for order in data}
    return data


async def watch_open_orders_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} watch open orders"
    logging.info(f"watching open orders for {name}")
    orders = await fetch_open_orders(client, {})
    if orders:
        push_data(db, "open_orders", name, orders)
    while True:
        update = await safe_timeout_method(
            client.watch_orders, log_str=log_str, timeout=600, fail_result={}
        )
        orders = update_orders(orders, update)
        push_data(db, "open_orders", name, orders)


async def watch_gateio_open_orders(
    client: ccxt.Exchange, db: redis.Redis, symbol: str, cache: OrderCache
) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} watch open orders"
    logging.info(f"watching open orders for {name} {symbol}")
    while True:
        update = await safe_timeout_method(
            client.watch_orders, symbol, log_str=log_str, timeout=600, fail_result={}
        )
        cache = update_orders(cache, update)
        push_data(db, "open_orders", name, cache)


async def watch_gateio_open_orders_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} watch open orders"
    logging.info(f"watching open orders for {log_str}")
    orders_cache: OrderCache = {}
    orders_cache = await fetch_open_orders(client, orders_cache)
    symbols_tasks = {}
    if orders_cache:
        push_data(db, "open_orders", name, orders_cache)
    while True:
        orders_cache = await fetch_open_orders(client, orders_cache)
        for symbol in orders_cache.keys():
            if symbol not in symbols_tasks:
                symbols_tasks[symbol] = asyncio.create_task(
                    watch_gateio_open_orders(client, db, symbol, orders_cache)
                )
        await asyncio.sleep(60)


async def main():
    """main function"""
    clients = get_clients()
    redis_db = redis.Redis(host="localhost", port=6379, db=0)
    tasks = start_open_orders_loop(clients, redis_db)
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logging.info("stopping")
    finally:
        for client in clients.values():
            await client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
