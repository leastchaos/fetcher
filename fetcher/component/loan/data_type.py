"""data type"""
from typing import TypedDict


class LoanDict(TypedDict):
    """loan dict"""
    timestamp: int
    amount: float
    asset: str
    id: str
    rate: float
    repaid: float
    repaid_interest: float
    unpaid_interest: float


LoanDictBySymbolById = dict[str, dict[str, LoanDict]]
