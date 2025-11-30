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
    """Transaction categories"""
    # Income categories (for credits ONLY) - just 2 options
    income = "income"        # ALL incoming money
    dividend = "dividend"    # Dividend from stocks only

    # Expense categories (for debits ONLY) - simplified major categories
    food = "food"                    # Groceries, dining, restaurants, food delivery
    bills = "bills"                  # Utilities, recharge, subscriptions, rent
    shopping = "shopping"            # Amazon, Flipkart, retail, online shopping
    transport = "transport"          # Uber, Ola, fuel, train, metro, auto
    health = "health"                # Healthcare, pharmacy, medical
    entertainment = "entertainment"  # Movies, streaming, gaming
    investment = "investment"        # Groww, Zerodha, mutual funds, stocks
    transfer = "transfer"            # UPI transfers to individuals
    emi = "emi"                      # Loan EMIs, credit card payments
    other = "other"                  # Anything that doesn't fit above


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
