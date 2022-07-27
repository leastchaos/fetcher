"""collect data from exchange and store in database"""
import asyncio

from fetcher.component.balance import start_balance_loop
from fetcher.client import get_clients
from fetcher.database import get_redis
from fetcher.utils import setup_logging

logger = setup_logging(__name__)


if __name__ == "__main__":
    exchanges = get_clients()
    database = get_redis()
    asyncio.run(start_balance_loop(exchanges, database))
