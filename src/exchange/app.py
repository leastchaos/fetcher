"""get data from database with flask"""
from itertools import product

from fastapi import APIRouter

from src.exchange.database import get_data, get_key, get_redis
from src.exchange.models.loans import Loan, NameSymbolIdLoan, SymbolIdLoan
from src.exchange.models.ticker import Ticker

from .models.balance import Balance, BalanceTicker

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


@app.get("/tickers")
def get_tickers() -> dict[str, Ticker]:
    """get all tickers"""
    redis_client = get_redis()
    keys = redis_client.scan(match="tickers::*", count=100)
    results = {}
    for key in keys[1]:
        data: dict[str, dict[str, float | str]] = get_data(redis_client, key)
        account_name = str(key, "utf-8").split("::")[1]
        results[account_name] = {}
        for symbol, ticker in data.items():
            results[account_name][symbol] = Ticker.parse_obj(ticker)
    return results


@app.get("/ticker/{exchange_name}/{symbol}", response_model=Ticker)
def get_ticker(exchange_name: str, symbol: str) -> Ticker:
    """get ticker"""
    redis_client = get_redis()
    key = get_key("tickers", exchange_name)
    symbol = symbol.replace("_", "/")
    return Ticker.parse_obj(get_data(redis_client, key)[symbol])


@app.get("/balance_tickers", response_model=dict[str, BalanceTicker])
def get_balance_tickers(
    quotes: list[str] = ["USD", "USDT", "BUSD", "USDC"]
) -> dict[str, BalanceTicker]:
    """get balance and tickers"""
    redis_client = get_redis()
    keys = redis_client.scan(match="balance::*", count=100)
    client_to_exchange = get_data(
        redis_client, get_key("client_to_exchange", "mapping")
    )
    tickers = get_tickers()
    balances = {}
    for key in keys[1]:
        data = get_data(redis_client, key)
        account_name = str(key, "utf-8").split("::")[1]
        exchange = client_to_exchange[account_name]
        data["price"] = {}
        for base, quote in product(data["total"], quotes):
            symbol = f"{base}/{quote}"
            if base not in data["price"]:
                data["price"][base] = {}
            if symbol in tickers[exchange]:
                data["price"][base][quote] = tickers[exchange][symbol]
        balances[account_name] = BalanceTicker.parse_obj(data)
    return balances
