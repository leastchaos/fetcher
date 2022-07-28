"""fetch kucoin loans"""
import logging

from src.exchange.component.loan.models import LoanDict, LoanDictSymbolId
from src.exchange.utils import safe_get_float, safe_timeout_method

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


def parse_loan(value: dict, update_time: float = None) -> LoanDict:
    """
    {
        "tradeId": "1231141",
        "currency": "USDT",
        "accruedInterest": "0.22121",
        "dailyIntRate": "0.0021",
        "liability": "1.32121",
        "maturityTime": "1544657947759",
        "principal": "1.22121",
        "repaidSize": "0",
        "term": 7,
        "createdAt": "1544657947759"
    }
    """
    return {
        "timestamp": update_time,
        "amount": safe_get_float(value, "principal"),
        "asset": value.get("currency"),
        "id": value.get("tradeId"),
        "rate": safe_get_float(value, "dailyIntRate", 0),
        "repaid": safe_get_float(value, "repaidSize", 0),
        "repaid_interest": 0,
        "unpaid_interest": safe_get_float(value, "accruedInterest", 0),
    }


async def fetch_kucoin_loan(client: ccxt.Exchange) -> LoanDictSymbolId:
    """update loan"""
    logging.info("fetching loan for %s", client.options["name"])
    loan: dict = await safe_timeout_method(
        client.private_get_margin_borrow_outstanding,
        {"pageSize": "50"},
    )
    if not loan and not loan.get("data", {}).get("items"):
        return []
    loans: list[dict] = loan.get("data", {}).get("items")
    loans_by_symbol_by_id: LoanDictSymbolId = {}
    for loan in loans:
        loan_dict = parse_loan(loan, client.milliseconds())
        symbol = loan_dict["asset"]
        if symbol not in loans_by_symbol_by_id:
            loans_by_symbol_by_id[symbol] = {}
        loans_by_symbol_by_id[symbol][loan_dict["id"]] = loan_dict
    return loans_by_symbol_by_id
