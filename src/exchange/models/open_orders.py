"""open orders model"""
from sqlmodel import SQLModel


class Fee(SQLModel):
    """fee model"""

    currency: str | None
    cost: float | None
    rate: float | None


class OpenOrder(SQLModel):
    """
    input:
    https://docs.ccxt.com/en/latest/manual.html?highlight=order#order-structure
    """

    id: str
    clientOrderId: str | None
    datetime: str | None
    lastTradeTimestamp: int | None
    symbol: str
    status: str
    side: str
    price: float
    remaining: float
    timestamp: int
    type: str | None
    timeInForce: str | None
    average: float | None
    filled: float | None
    cost: float | None
    trades: list | None
    fee: Fee | None
