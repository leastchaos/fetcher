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

    @classmethod
    def dummy(cls, symbol: str) -> "Ticker":
        """dummy"""
        return Ticker(
            ask=0,
            askVolume=0,
            average=0,
            baseVolume=0,
            bid=0,
            bidVolume=0,
            change=0,
            close=0,
            datetime="",
            high=0,
            last=0,
            low=0,
            open=0,
            percentage=0,
            previousClose=0,
            quoteVolume=0,
            symbol=symbol,
            timestamp=0,
            vwap=0,
        )
