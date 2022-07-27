"""collect data from exchange and store in database"""
import asyncio
import logging

from src.exchange.client import get_clients
from src.exchange.component.balance import start_balance_loop
from src.exchange.component.loan import start_loans_loop
from src.exchange.database import get_redis
from src.exchange.utils import setup_logging


async def main():
    """main"""
    setup_logging()
    redis_client = get_redis()
    clients = get_clients()
    tasks = []
    tasks.extend(start_balance_loop(clients, redis_client))
    tasks.extend(start_loans_loop(clients, redis_client))
    try:
        await asyncio.gather(*tasks)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logging.info("shutting down")
    finally:
        await asyncio.gather(*[client.close() for client in clients.values()])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
