"""balance model"""
from sqlmodel import SQLModel


class Balance(SQLModel):
    """balance model"""

    free: dict[str, float | None]
    used: dict[str, float | None]
    total: dict[str, float | None]
    timestamp: int
