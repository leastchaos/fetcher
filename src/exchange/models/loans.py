"""loan model"""
from sqlmodel import SQLModel


class Loan(SQLModel):
    """loan model"""

    timestamp: int
    amount: float | None
    asset: str
    id: str
    rate: float | None
    repaid: float | None
    repaid_interest: float | None
    unpaid_interest: float | None


Symbol = str
Id = str
Name = str
SymbolIdLoan = dict[Symbol, dict[Id, Loan]]
NameSymbolIdLoan = dict[Name, dict[Symbol, dict[Id, Loan]]]
