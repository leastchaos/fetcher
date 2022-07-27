from typing import Awaitable, Callable
from fetcher.component.loan.data_type import LoanDictBySymbolById
from fetcher.component.loan.kucoin import fetch_kucoin_loan
from .gateio import fetch_gateio_cross_loan, fetch_gateio_isolated_loan

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


loan_methods = {
    ("gateio", "margin", "cross"): fetch_gateio_cross_loan,
    ("gateio", "margin", "isolated"): fetch_gateio_isolated_loan,
    ("kucoin", "margin", "cross"): fetch_kucoin_loan,
    ("kucoin", "margin", "isolated"): fetch_kucoin_loan,
}

def get_loan_method(client: ccxt.Exchange) -> Callable[[ccxt.Exchange], Awaitable[LoanDictBySymbolById]]:
    """get loan method"""
    exchange_name = client.id
    market_type = client.options["defaultType"]
    margin_mode = client.options["marginMode"]
    return loan_methods[(exchange_name, margin_mode, market_type)]

async def fetch_loans_loop(client: ccxt.Exchange) -> None:
    """fetch loans"""
    