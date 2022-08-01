"""get data from database with flask"""
from itertools import chain
from statistics import median

from fastapi import APIRouter, Query

from src.exchange.app.open_orders import app as open_orders_app
from src.exchange.database import get_data, get_key, get_redis
from src.exchange.models.balance import AccountInfo, Balance
from src.exchange.models.loans import IdLoan, Loan, NameSymbolIdLoan, SymbolIdLoan
from src.exchange.models.positions import Position
from src.exchange.models.ticker import Ticker

app = APIRouter(prefix="/exchange", tags=["exchange"])
app.include_router(open_orders_app)


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
def get_tickers(exchange: str = None) -> dict[str, Ticker]:
    """get all tickers"""
    redis_client = get_redis()
    keys = redis_client.scan(match="tickers::*", count=100)
    if exchange:
        keys = [0, [bytes(f"tickers::{exchange}", "utf8")]]
    results = {}
    for key in keys[1]:
        data: dict[str, dict[str, float | str]] = get_data(redis_client, key)
        account_name = str(key, "utf-8").split("::")[1]
        results[account_name] = {}
        for symbol, ticker in data.items():
            results[account_name][symbol] = Ticker.parse_obj(ticker)
    return results


@app.get("/ticker/{account_name}/{symbol}", response_model=Ticker)
def get_ticker(account_name: str, symbol: str) -> Ticker:
    """get ticker"""
    redis_client = get_redis()
    key = get_key("tickers", account_name)
    symbol = symbol.replace("_", "/").replace("%3", ":").split("-")[0]
    try:
        return Ticker.parse_obj(get_data(redis_client, key)[symbol])
    except Exception:
        symbol = symbol.split(":")[0]
        return Ticker.parse_obj(get_data(redis_client, key)[symbol])


def get_ticker_price(ticker: Ticker) -> float:
    """get ticker price"""
    return ticker.last or ticker.close or ticker.bid or ticker.ask or 0


def get_avg_price(tickers: dict[str, Ticker], base: str, quotes: list[str]) -> float:
    """get average price"""
    if base in quotes:
        return 1
    symbols = [f"{base}/{quote}" for quote in quotes] + [
        f"{base}/{quote}:{quote}" for quote in quotes
    ]
    prices = [
        get_ticker_price(tickers[symbol]) for symbol in symbols if symbol in tickers
    ]
    if not prices:
        return 0
    return median(prices)


def get_loan_amount(loans: IdLoan) -> float:
    """get loan amount"""

    def get_amount(loan: Loan) -> float:
        amount = loan.amount or 0
        repaid = loan.repaid or 0
        unpaid_interest = loan.unpaid_interest or 0
        return amount - repaid + unpaid_interest

    return sum(get_amount(loan) for loan in loans.values())


@app.get("/account_infos", response_model=dict[str, AccountInfo])
def get_account_infos(
    quotes: list[str] = Query(default=["USD", "USDT", "BUSD", "USDC"])
) -> dict[str, AccountInfo]:
    """get balance and tickers"""
    redis_client = get_redis()
    keys = redis_client.scan(match="balance::*", count=100)
    tickers = get_tickers()
    loans = get_loans()
    balances = {}
    for key in keys[1]:
        data = get_data(redis_client, key)
        account_name = str(key, "utf-8").split("::")[1]
        loan = loans.get(account_name, {})
        ticker = tickers.get(account_name.split("-")[0], {})
        data["price"] = {
            base: get_avg_price(ticker, base, quotes)
            for base in chain(data["total"], loan)
        }
        data["loan"] = {base: get_loan_amount(loan.get(base, {})) for base in loan}
        balances[account_name] = AccountInfo.parse_obj(data)
    return balances


@app.get("/positions", response_model=dict[str, dict[str, list[Position]]])
def get_positions() -> dict[str, dict[str, list[Position]]]:
    """get all positions"""
    redis_client = get_redis()
    keys = redis_client.scan(match="positions::*", count=100)
    positions = {}
    for key in keys[1]:
        data = get_data(redis_client, key)
        account_name = str(key, "utf-8").split("::")[1]
        positions[account_name] = data
    return positions
