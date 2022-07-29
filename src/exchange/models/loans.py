"""loan model"""
from typing import TypedDict

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


class LoanDict(TypedDict):
    """loan dict"""

    timestamp: int
    amount: float | None
    asset: str
    id: str
    rate: float | None
    repaid: float | None
    repaid_interest: float | None
    unpaid_interest: float | None


Asset = str
Id = str
Name = str
IdLoan = dict[Id, Loan]
SymbolIdLoan = dict[Asset, dict[Id, Loan]]
NameSymbolIdLoan = dict[Name, dict[Asset, dict[Id, Loan]]]
