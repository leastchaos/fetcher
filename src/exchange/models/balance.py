"""balance model"""
from sqlmodel import SQLModel

from src.exchange.models.ticker import Ticker


class Balance(SQLModel):
    """balance model"""

    free: dict[str, float | None]
    used: dict[str, float | None]
    total: dict[str, float | None]
    timestamp: int


class BalanceTicker(Balance):
    """balance model with ticker"""

    price: dict[str, dict[str, Ticker]]
