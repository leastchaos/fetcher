import asyncio
import logging
from typing import Awaitable, Callable

import ccxt.async_support as ccxt
import redis

from src.exchange.component.loan.kucoin import fetch_kucoin_loan
from src.exchange.models.loans import SymbolIdLoan
from src.exchange.utils import push_data, safe_timeout_method

from .gateio import fetch_gateio_cross_loan, fetch_gateio_isolated_loan

loan_methods = {
    ("gateio", "spot", "cross"): fetch_gateio_cross_loan,
    ("gateio", "spot", "isolated"): fetch_gateio_isolated_loan,
    ("kucoin", "margin", "cross"): fetch_kucoin_loan,
    ("kucoin", "margin", "isolated"): fetch_kucoin_loan,
}


def get_loan_method(
    client: ccxt.Exchange,
) -> Callable[[ccxt.Exchange], Awaitable[SymbolIdLoan]] | None:
    """get loan method"""
    exchange_name = client.id
    market_type = client.options.get("defaultType")
    margin_mode = client.options.get("defaultMarginMode")
    key = (exchange_name, market_type, margin_mode)
    method = loan_methods.get(key)
    return method


async def fetch_loans_loop(client: ccxt.Exchange, db: redis.Redis) -> None:
    """fetch loans"""
    method = get_loan_method(client)
    if method is None:
        return
    name = client.options["name"]
    log_str = f"{name} fetch loans"
    logging.info(f"fetching loans for {name}: {method.__name__}")
    while True:
        loans = await safe_timeout_method(
            method, client, log_str=log_str, fail_result={}
        )
        if method == fetch_gateio_isolated_loan:
            for market, loans_dict in loans.items():
                push_data(db, "loan", f"{name}-{market}", loans_dict)
            continue
        if loans:
            push_data(db, "loan", name, loans)
        await asyncio.sleep(60)


def start_loans_loop(clients: ccxt.Exchange, db: redis.Redis) -> list[asyncio.Task]:
    """start loans loop"""
    return [
        asyncio.create_task(fetch_loans_loop(client, db)) for client in clients.values()
    ]
