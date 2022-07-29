"""ticker model"""
from sqlmodel import SQLModel


class Ticker(SQLModel):
    ask: float | None
    askVolume: float | None
    average: float | None
    baseVolume: float | None
    bid: float | None
    bidVolume: float | None
    change: float | None
    close: float | None
    datetime: str | None
    high: float | None
    last: float | None
    low: float | None
    open: float | None
    percentage: float | None
    previousClose: float | None
    quoteVolume: float | None
    symbol: str
    timestamp: int
    vwap: float | None
