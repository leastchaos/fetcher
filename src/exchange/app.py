"""get data from database with flask"""
import time

from fastapi import APIRouter

from src.exchange.database import get_data, get_key, get_redis

from .models.balance_model import Balance, Balances

app = APIRouter(prefix="/exchange", tags=["exchange"])


def parse_balance(balance: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """delete all asset that is equal to 0"""
    assets_to_delete = [
        asset for asset, value in balance["total"].items() if value == 0
    ]
    for asset in assets_to_delete:
        del balance["total"][asset]
        del balance["free"][asset]
        del balance["used"][asset]
    return balance


@app.get("/balance/{account_name}", response_model=Balance)
def get_balance(account_name: str) -> Balance:
    """get balance"""
    redis_client = get_redis()
    key = get_key("balance", account_name)
    data = get_data(redis_client, key)
    data = parse_balance(data)
    return Balance.parse_obj(data)


@app.get("/balances", response_model=list[Balances])
def get_balances() -> dict[str, dict[str, dict[str, float] | float]]:
    """get all balance"""
    redis_client = get_redis()
    keys = redis_client.scan(match="balance::*", count=100)
    balances = []
    for key in keys[1]:
        data = get_data(redis_client, key)
        data = parse_balance(data)
        balances.append(
            Balances(
                account_name=str(key, "utf-8").split("::")[1],
                balance=Balance.parse_obj(data),
                timestamp=time.time(),
            )
        )
    return balances


@app.get("/loan/{account_name}")
def get_loan(account_name: str) -> dict[str, dict[str, float] | float]:
    """get loan"""
    redis_client = get_redis()
    key = get_key("loan", account_name)
    print(get_data(redis_client, key))
    return get_data(redis_client, key)


@app.get("/loans")
def get_loans() -> dict[str, dict[str, dict[str, float] | float]]:
    """get all loan"""
    redis_client = get_redis()
    keys = redis_client.scan(match="loan::*", count=100)
    data = {}
    for key in keys[1]:
        data[str(key, "UTF-8").split("::")[1]] = get_data(redis_client, key)
    return data
