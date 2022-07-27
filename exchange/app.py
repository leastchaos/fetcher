"""get data from database with flask"""
from fastapi import APIRouter

from exchange.database import get_data, get_key, get_redis

app = APIRouter(prefix="/exchange", tags=["exchange"])


@app.get("/balance/{account_name}")
def get_balance(account_name: str) -> dict[str, dict[str, float] | float]:
    """get balance"""
    redis_client = get_redis()
    key = get_key("balance", account_name)
    return get_data(redis_client, key)


@app.get("/balances")
def get_balances() -> dict[str, dict[str, dict[str, float] | float]]:
    """get all balance"""
    redis_client = get_redis()
    keys = redis_client.scan(match="balance::*", count=100)
    data = {}
    for key in keys[1]:
        data[str(key).split("::")[1]] = get_data(redis_client, key)
    return data


@app.get("/loan/{account_name}")
def get_loan(account_name: str) -> dict[str, dict[str, float] | float]:
    """get loan"""
    redis_client = get_redis()
    key = get_key("loan", account_name)
    return get_data(redis_client, key)


@app.get("/loans")
def get_loans() -> dict[str, dict[str, dict[str, float] | float]]:
    """get all loan"""
    redis_client = get_redis()
    keys = redis_client.scan(match="loan::*", count=100)
    data = {}
    for key in keys[1]:
        data[str(key).split("::")[1]] = get_data(redis_client, key)
    return data
