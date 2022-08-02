"""fetch tickers"""
import asyncio
import logging

import ccxt.async_support as ccxt
import redis

from src.exchange.component.client import get_clients
from src.exchange.models.positions import Position, PositionDict
from src.exchange.utils import push_data, safe_timeout_method


def parse_positions(positions: list[PositionDict]) -> dict[str, list[PositionDict]]:
    """parse positions"""
    result: dict[str, list[PositionDict]] = {}
    for position in positions:
        try:
            if position["contracts"] == 0:
                continue
            if position["side"] == "short":
                position["contracts"] = -(abs(position["contracts"]) or 0)
            if position["symbol"] not in result:
                result[position["symbol"]] = []
            position = Position.parse_obj(position).dict()
            result[position["symbol"]].append(position)
        except Exception as err:
            print(positions)
            logging.exception(f"parse position error: {err}")
            raise
    return result


async def fetch_positions_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """fetch loans"""
    name = client.options["name"]
    log_str = f"{name} fetch positions"
    if not client.has.get("fetchPositions"):
        logging.info(f"{name} does not support fetchPositions")
        return
    if client.options["defaultType"] not in ["swap", "future"]:
        return
    try:
        await client.fetch_positions()
    except ccxt.errors.NotSupported as err:
        logging.info(f"{name} does not support fetchPositions: {err}")
        return
    logging.info(f"fetching positions for {name}")
    data = {}
    while True:
        data = await safe_timeout_method(
            client.fetch_positions, fail_result=data, log_str=log_str
        )
        parsed_data = parse_positions(data)
        push_data(db, "positions", name, parsed_data)
        await asyncio.sleep(1)


def start_positions_loop(
    clients: dict[str, ccxt.Exchange], db: redis.Redis
) -> list[asyncio.Task]:
    """start loans loop"""
    return [
        asyncio.create_task(fetch_positions_loop(client, db))
        for client in clients.values()
    ]


async def main():
    """main"""
    logging.basicConfig(level=logging.INFO)
    redis_db = redis.Redis()
    clients = get_clients()
    tasks = start_positions_loop(clients, redis_db)
    try:
        await asyncio.gather(*tasks)
    finally:
        for client in clients.values():
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
