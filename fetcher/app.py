"""get data from database with flask"""

from flask import Flask

from fetcher.database import get_data, get_key, get_redis

app = Flask(__name__)

@app.get('/balance/<account_name>')
def get_balance(account_name: str) -> dict[str, dict[str, float] | float]:
    """get balance"""
    redis_client = get_redis()
    key = get_key("balance", account_name)
    return get_data(redis_client, key)
