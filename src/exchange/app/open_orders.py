from fastapi import APIRouter

from src.exchange.database import get_data, get_key, get_redis
from src.exchange.models.orders import Order

app = APIRouter(prefix="/open_orders", tags=["exchange", "account_infos"])


@app.get("/", response_model=dict[str, dict[str, dict[str, Order]]])
def get_open_orders() -> dict[str, dict[str, Order]]:
    """get open orders"""
    redis_client = get_redis()
    keys = redis_client.scan(match="open_orders::*", count=100)
    orders = {}
    for key in keys[1]:
        data = get_data(redis_client, key)
        account_name = str(key, "utf-8").split("::")[1]
        orders[account_name] = {}
        for symbol, orders_dict in data.items():
            orders[account_name][symbol] = {}
            for order_id, order in orders_dict.items():
                orders[account_name][symbol][order_id] = Order.parse_obj(order)
    return orders


@app.get("/{account_name}", response_model=dict[str, dict[str, Order]])
def get_open_orders_by_account_name(account_name: str) -> dict[str, Order]:
    """get open orders"""
    redis_client = get_redis()
    key = get_key("open_orders", account_name)
    data = get_data(redis_client, key)
    orders = {}
    for symbol, orders_dict in data.items():
        orders[symbol] = {}
        for order_id, order in orders_dict.items():
            orders[symbol][order_id] = Order.parse_obj(order)
    return orders


@app.get("/{account_name}/{symbol}", response_model=dict[str, Order])
def get_open_orders_by_account_name_and_symbol(
    account_name: str, symbol: str
) -> dict[str, Order]:
    """get open orders"""
    redis_client = get_redis()
    key = get_key("open_orders", account_name)
    data = get_data(redis_client, key)
    orders = {}
    for order_id, order in data.items():
        orders[order_id] = Order.parse_obj(order)
    return orders


@app.get("/{account_name}/{symbol}/{order_id}", response_model=Order)
def get_open_orders_by_account_name_and_symbol_and_order_id(
    account_name: str, symbol: str, order_id: str
) -> Order:
    """get open orders"""
    redis_client = get_redis()
    key = get_key("open_orders", account_name)
    data = get_data(redis_client, key)
    order = data.get(symbol, {}).get(order_id, {})
    return Order.parse_obj(order)
