"""handle trade operation"""
from typing import Literal

from fastapi import APIRouter

from src.exchange.app.open_orders import get_open_orders_by_account_name
from src.exchange.component.client import get_clients

app = APIRouter(prefix="/trade", tags=["exchange", "trade"])
available_accounts = Literal[tuple(get_clients().keys())]


@app.get("/available_accounts")
def get_available_accounts() -> list[str]:
    """get available accounts"""
    return get_clients().keys()


@app.post("/create_order")
async def create_order(
    account_name: available_accounts,
    symbol: str,
    side: Literal["buy", "sell"],
    type: Literal["limit", "market"],
    amount: float,
    price: float,
    params: dict | None = None,
) -> dict[str, str]:
    """create order"""
    client = get_clients()[account_name]
    if params is None:
        params = {}
    order = await client.create_order(symbol, type, side, amount, price, params)
    return order


@app.post("/cancel_order")
async def cancel_order(account_name: str, symbol: str, order_id: str) -> dict[str, str]:
    """cancel order"""
    client = get_clients()[account_name]
    order = await client.cancel_order(order_id, symbol)
    return order


@app.post("/cancel_all_orders")
async def cancel_all_orders(
    account_name: str, symbol: str | None, params: dict | None = None
) -> dict[str, str]:
    """cancel all orders"""
    client = get_clients()[account_name]
    if params is None:
        params = {}
    if client.has.get("cancelAllOrders"):
        return await client.cancel_all_orders(symbol=symbol, params=params)
    orders = get_open_orders_by_account_name(account_name)
    results = []
    for order_id, order in orders.items():
        if symbol is None or order.symbol == symbol:
            order = await client.cancel_order(order_id, order.symbol)
        results.append(order)
    return results
