import asyncio
import logging
from typing import Awaitable, Callable

import redis

from exchange.component.loan.data_type import LoanDictBySymbolById
from exchange.component.loan.kucoin import fetch_kucoin_loan
from exchange.utils import push_data, safe_timeout_method

from .gateio import fetch_gateio_cross_loan, fetch_gateio_isolated_loan

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


loan_methods = {
    ("gateio", "spot", "cross"): fetch_gateio_cross_loan,
    ("gateio", "spot", "isolated"): fetch_gateio_isolated_loan,
    ("kucoin", "margin", "cross"): fetch_kucoin_loan,
    ("kucoin", "margin", "isolated"): fetch_kucoin_loan,
}


def get_loan_method(
    client: ccxt.Exchange,
) -> Callable[[ccxt.Exchange], Awaitable[LoanDictBySymbolById]] | None:
    """get loan method"""
    exchange_name = client.id
    market_type = client.options.get("defaultType")
    margin_mode = client.options.get("defaultMarginMode")
    key = (exchange_name, market_type, margin_mode)
    method = loan_methods.get(key)
    logging.info("%s loan method: %s", key, method)
    return method


async def fetch_loans_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """fetch loans"""
    method = get_loan_method(client)
    if method is None:
        return
    name = client.options["name"]
    while True:
        loans = await safe_timeout_method(method, client)
        if loans:
            push_data(db, "loan", name, loans)
        await asyncio.sleep(60)


def start_loans_loop(clients: ccxt.Exchange, db: redis.Redis) -> list[asyncio.Task]:
    """start loans loop"""
    return [
        asyncio.create_task(fetch_loans_loop(client, db)) for client in clients.values()
    ]
