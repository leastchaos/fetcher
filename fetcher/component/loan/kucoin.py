"""fetch kucoin loans"""
from fetcher.component.loan.data_type import LoanDict, LoanDictBySymbolById
from fetcher.utils import safe_get_float, safe_timeout_method, setup_logging

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


logger = setup_logging(__name__)


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


async def fetch_kucoin_loan(client: ccxt.Exchange) -> LoanDictBySymbolById:
    """update loan"""
    logger.info("fetching loan for %s", client.account_name)
    loan: dict = await safe_timeout_method(
        client.private_get_margin_borrow_outstanding, {"pageSize": "500"}, logger=logger
    )
    if not loan and not loan.get("data", {}).get("items"):
        return []
    loans: list[dict] = loan.get("data", {}).get("items")
    loans_by_symbol_by_id: LoanDictBySymbolById = {}
    for loan in loans:
        loan_dict = parse_loan(loan, update_time=loan.get("createdAt"))
        symbol = loan_dict["asset"]
        if symbol not in loans_by_symbol_by_id:
            loans_by_symbol_by_id[symbol] = {}
        loans_by_symbol_by_id[symbol][loan_dict["id"]] = loan_dict
    return loans_by_symbol_by_id
