"""balance model"""
from sqlmodel import SQLModel


class Balance(SQLModel):
    """
    free, used, total: return dictionary of {asset: amount}
    """

    free: dict[str, float | None]
    used: dict[str, float | None]
    total: dict[str, float | None]
    timestamp: int


class AccountInfo(Balance):
    """
    price: return dictionary of {asset: {quote: ticker}}
    loan: return dictionary of {asset: {id: loan}}
    """

    price: dict[str, float]
    loan: dict[str, float]
