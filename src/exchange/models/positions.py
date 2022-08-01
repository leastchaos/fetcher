from typing import Any, TypedDict

from sqlmodel import SQLModel


class PositionDict(TypedDict):
    info: Any
    id: str
    symbol: str
    timestamp: int
    datetime: str
    isolated: bool
    hedged: bool
    side: str
    contracts: float
    contractSize: float
    entryPrice: float
    markPrice: float
    notional: float
    leverage: float
    collateral: float
    initialMargin: float
    maintenanceMargin: float
    initialMarginPercentage: float
    maintenanceMarginPercentage: float
    unrealizedPnl: float
    liquidationPrice: float
    marginMode: str
    percentage: float


class Position(SQLModel):
    id: str | None
    symbol: str
    timestamp: int | None
    datetime: str | None
    isolated: bool | None
    hedged: bool | None
    side: str
    contracts: float
    contractSize: float
    entryPrice: float | None
    markPrice: float
    notional: float | None
    leverage: float | None
    collateral: float | None
    initialMargin: float | None
    maintenanceMargin: float | None
    initialMarginPercentage: float | None
    maintenanceMarginPercentage: float | None
    unrealizedPnl: float | None
    liquidationPrice: float | None
    marginMode: str | None
    percentage: float | None
