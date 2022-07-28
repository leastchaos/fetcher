"""get data from database with flask"""
from fastapi import APIRouter

from src.exchange.database import get_data, get_key, get_redis
from src.exchange.models.loans import Loan, NameSymbolIdLoan, SymbolIdLoan

from .models.balance import Balance

app = APIRouter(prefix="/exchange", tags=["exchange"])


@app.get("/balance/{account_name}", response_model=Balance)
def get_balance(account_name: str) -> Balance:
    """get balance"""
    redis_client = get_redis()
    key = get_key("balance", account_name)
    data = get_data(redis_client, key)
    return Balance.parse_obj(data)


@app.get("/balances", response_model=dict[str, Balance])
def get_balances() -> dict[str, Balance]:
    """get all balance"""
    redis_client = get_redis()
    keys = redis_client.scan(match="balance::*", count=100)
    balances = {}
    for key in keys[1]:
        data = get_data(redis_client, key)
        balances[str(key, "utf-8").split("::")[1]] = Balance.parse_obj(data)
    return balances


@app.get("/loan/{account_name}", response_model=SymbolIdLoan)
def get_loan(account_name: str) -> SymbolIdLoan:
    """get loan"""
    redis_client = get_redis()
    key = get_key("loan", account_name)
    return {
        symbol: {id: Loan.parse_obj(data) for id, data in symbol_loans.items()}
        for symbol, symbol_loans in get_data(redis_client, key).items()
    }


@app.get("/loans", response_model=NameSymbolIdLoan)
def get_loans() -> NameSymbolIdLoan:
    """get all loan"""
    redis_client = get_redis()
    keys = redis_client.scan(match="loan::*", count=100)
    account_names = [str(key, "utf-8").split("::")[1] for key in keys[1]]
    return {account_name: get_loan(account_name) for account_name in account_names}
