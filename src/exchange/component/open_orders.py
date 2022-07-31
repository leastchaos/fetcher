"""collect open order data from exchange and store in database"""
import asyncio
import logging
from typing import Any

import redis

from src.exchange.component.client import get_clients
from src.exchange.models.open_orders import OpenOrder
from src.exchange.utils import push_data, safe_timeout_method

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt

OrderCache = dict[str, dict[str, dict[str, OpenOrder]]]


def parse_open_order(open_order: dict[str, Any]) -> OpenOrder:
    """parse open orders"""
    return OpenOrder.parse_obj(open_order).dict()


def start_open_orders_loop(
    clients: dict[str, ccxt.Exchange], redis_db: redis.Redis
) -> list[asyncio.Task]:
    """collect data from exchange and store in database"""
    tasks = []
    for client in clients.values():
        if client.has.get("watchOrders"):
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


async def watch_open_orders_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """collect data from exchange and store in database"""
    name = client.options["name"]
    log_str = f"{name} watch open orders"
    logging.info(f"watching open orders for {name}")
    orders = []
    try:
        orders = await client.fetch_open_orders()
    except Exception as err:
        logging.error("%s error: %s", log_str, err)
    orders = {
        order["symbol"]: {order["id"]: parse_open_order(order)} for order in orders
    }
    if orders:
        push_data(db, "open_orders", name, orders)
    while True:
        try:
            update = await safe_timeout_method(
                client.watch_orders, log_str=log_str, timeout=600, fail_result={}
            )
        except Exception as err:
            logging.error("%s error: %s", log_str, err)
            return
        for order in update:
            if order["symbol"] not in orders:
                orders[order["symbol"]] = {}
            if order["status"] == "open":
                orders[order["symbol"]][order["id"]] = parse_open_order(order)
            else:
                orders[order["symbol"]].pop(order["id"], None)
        push_data(db, "open_orders", name, orders)


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
