"""
Pydantic schemas for OpenAI Structured Outputs.
These models guarantee 100% JSON compliance from GPT.
"""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type - money in or out"""
    credit = "credit"
    debit = "debit"


class Category(str, Enum):
    """Transaction categories - both income and expense categories"""
    # Income categories (for credits)
    salary = "salary"
    freelance = "freelance"
    interest = "interest"
    dividend = "dividend"
    refund = "refund"
    cashback = "cashback"

    # Expense categories (for debits)
    groceries = "groceries"
    utilities = "utilities"
    rent = "rent"
    entertainment = "entertainment"
    dining = "dining"
    transportation = "transportation"
    fuel = "fuel"
    healthcare = "healthcare"
    shopping = "shopping"
    education = "education"
    insurance = "insurance"
    subscriptions = "subscriptions"
    investment = "investment"
    transfer = "transfer"
    fees = "fees"
    emi = "emi"
    recharge = "recharge"
    other = "other"


class Transaction(BaseModel):
    """Single transaction from bank statement"""
    date: str
    description: str
    category: Category
    amount: float
    type: TransactionType


class FinancialExtraction(BaseModel):
    """
    GPT's extraction result.
    Using Optional for fields that might not be found in the document.
    """
    is_financial_statement: bool
    opening_balance: Optional[float]
    closing_balance: Optional[float]
    transactions: List[Transaction]
