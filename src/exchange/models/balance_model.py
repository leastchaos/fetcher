"""balance model"""
from sqlmodel import Field, SQLModel


class Balance(SQLModel):
    """balance model"""

    free: dict[str, float | None]
    used: dict[str, float | None]
    total: dict[str, float | None]
    timestamp: int


class Balances(SQLModel, table=True):
    """balances model"""

    account_name: str = Field(primary_key=True)
    balance: Balance
    timestamp: int
