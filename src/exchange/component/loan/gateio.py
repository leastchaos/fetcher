"""fetch gateio loan"""
from src.exchange.component.loan.models import LoanDict, LoanDictSymbolId
from src.exchange.utils import safe_get_float, safe_get_float_2

try:
    import ccxtpro as ccxt
except ImportError:
    import ccxt.async_support as ccxt


def parse_loan(value: dict, update_time: float = None) -> LoanDict:
    """
    loans structure

    gateio cross margin
    {'amount': '1931.417',
    'create_time': '1648477520881',
    'currency': 'EXRD',
    'id': '1308017',
    'repaid': '0',
    'repaid_interest': '0',
    'status': '2',
    'text': 'apiv4',
    'unpaid_interest': '0.769508723069',
    'update_time': '1648681217328'}

    gateio isolated margin loan
    {'amount': '400',
    'auto_renew': True,
    'create_time': '1647871100',
    'currency': 'DAO',
    'currency_pair': 'DAO_USDT',
    'days': '10',
    'expire_time': '1648735101',
    'id': '31822993',
    'left': '0',
    'paid_interest': '0',
    'rate': '0.0001',
    'repaid': '0',
    'side': 'borrow',
    'status': 'loaned',
    'unpaid_interest': '0.376666666669'}
    """
    return {
        "timestamp": safe_get_float(value, "update_time", update_time),
        "amount": safe_get_float(value, "amount"),
        "asset": value.get("currency"),
        "id": value.get("id"),
        "rate": safe_get_float(value, "rate"),
        "repaid": safe_get_float(value, "repaid"),
        "repaid_interest": safe_get_float_2(value, "repaid_interest", "paid_interest"),
        "unpaid_interest": safe_get_float(value, "unpaid_interest"),
    }


async def fetch_gateio_cross_loan(client: ccxt.gateio) -> LoanDictSymbolId:
    """watch ccxt loans and update self._loans"""
    if not hasattr(fetch_gateio_cross_loan, "loan_details"):
        fetch_gateio_cross_loan.loan_details = {}
    loans: list[dict] = await client.private_margin_get_cross_loans(
        params={"status": 2}
    )
    completed_loans: list[dict] = await client.private_margin_get_cross_loans(
        params={"status": 3}
    )
    loans.extend(completed_loans)
    loans_cache: LoanDictSymbolId = {}
    for loan in loans:
        currency = loan["currency"]
        if currency not in fetch_gateio_cross_loan.loan_details:
            fetch_gateio_cross_loan.loan_details[
                currency
            ] = await client.public_margin_get_cross_currencies_currency(
                params={"currency": currency}
            )
        if currency not in loans_cache:
            loans_cache[currency] = {}
        loan_detail = fetch_gateio_cross_loan.loan_details[currency]
        loan.update(loan_detail)
        unified_loan = parse_loan(loan, client.milliseconds())
        loans_cache[currency][unified_loan["id"]] = unified_loan

    return loans_cache


async def fetch_gateio_isolated_loan(client: ccxt.gateio) -> LoanDictSymbolId:
    """watch ccxt loans and update self._loans"""
    if not hasattr(fetch_gateio_cross_loan, "loan_details"):
        fetch_gateio_cross_loan.loan_details = {}
    loans: list[dict] = await client.private_margin_get_cross_loans(
        params={"status": 2}
    )
    completed_loans: list[dict] = await client.private_margin_get_cross_loans(
        params={"status": 3}
    )
    loans.extend(completed_loans)
    loans_cache: LoanDictSymbolId = {}
    for loan in loans:
        currency = loan["currency"]
        if currency not in fetch_gateio_cross_loan.loan_details:
            fetch_gateio_cross_loan.loan_details[
                currency
            ] = await client.public_margin_get_cross_currencies_currency(
                params={"currency": currency}
            )
        if currency not in loans_cache:
            loans_cache[currency] = {}
        loan_detail = fetch_gateio_cross_loan.loan_details[currency]
        loan.update(loan_detail)
        unified_loan = parse_loan(loan, client.milliseconds())
        loans_cache[currency][unified_loan["id"]] = unified_loan

    return loans_cache
