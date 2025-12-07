"""
LLM Processor Service - Hybrid Approach
Transactions are parsed by Python. LLM only categorizes descriptions.
This reduces token usage by ~90% and improves accuracy.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

from services.schemas import Category, CategoryBatch

load_dotenv()

# Setup logging
logger = logging.getLogger('llm_processor')

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CATEGORIZATION_PROMPT = """You are a financial transaction categorizer.
Given a list of transaction descriptions with their type (credit/debit), assign the correct category to each.

CATEGORY RULES:

For type="credit" (money coming IN), use ONLY:
- income: ALL incoming money (salary, NEFT, interest, refunds, transfers IN, dividends from companies)
- dividend: ONLY if description explicitly contains "DIVIDEND" or "DIV"

For type="debit" (money going OUT), use:
- food: Groceries (DMart, BigBasket, AVENUE SUPERMARTS, RELIANCE SMART), restaurants, Swiggy, Zomato, snacks, food plaza
- bills: Utilities, JIO/Airtel recharge, subscriptions (Claude.ai, Google, OpenAI), rent (ZOLOSTAYS), CBDT (tax)
- shopping: Amazon, Flipkart, online shopping, retail stores
- transport: Uber, Ola, INDIAN RAILWAYS, IRCTC, REDBUS, PMPML, INDIGO (airline), metro, fuel
- health: Hospitals, pharmacies, WELLNESS, MEDICAL, healthcare
- entertainment: Movies, Netflix, Prime, Spotify, gaming
- investment: Groww, Zerodha, NEXTBILLION TECHNOLO, mutual funds, stocks purchases
- transfer: UPI transfers to individual person names (like PRAKASHCHAND, RAHUL, personal names)
- emi: EMI payments, loan repayments, BAJAJ FINANCE
- other: ONLY if nothing else fits (bank charges, forex markup, unknown)

IMPORTANT:
- Look at the transaction TYPE first before categorizing
- Credits should almost always be "income" (or "dividend" if explicitly stated)
- Person names in debits = "transfer" (money sent to someone)
- Company names in debits = categorize by company type
- CLIMATEFORCE, NEXTBILLION = income (salary from employer)
- ACHC entries with company names (TCS, INFOSYS, IRFC, APTUS, HUL) = dividend income
- ATW = ATM withdrawal = transfer
- INTEREST PAID = income"""


async def categorize_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Categorize transactions using LLM.
    Only sends descriptions and types, receives categories back.

    Args:
        transactions: List of parsed transactions with date, description, amount, type

    Returns:
        Same transactions with category field filled
    """
    if not transactions:
        return transactions

    logger.info(f"Categorizing {len(transactions)} transactions via LLM")

    # Build compact input for LLM
    # Format: index|type|description
    transaction_list = []
    for i, txn in enumerate(transactions):
        desc = txn.get('description', '')[:100]  # Limit description length
        txn_type = txn.get('type', 'debit')
        transaction_list.append(f"{i}|{txn_type}|{desc}")

    input_text = "\n".join(transaction_list)

    user_prompt = f"""Categorize each transaction. Return the index and category for each.

Transactions (format: index|type|description):
{input_text}

Assign a category to each transaction based on the rules."""

    try:
        response = await client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": CATEGORIZATION_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            text_format=CategoryBatch
        )

        parsed_result: Optional[CategoryBatch] = response.output_parsed

        if parsed_result is None:
            logger.warning("LLM returned no parsed result, using fallback categories")
            # Fallback: assign default categories based on type
            for txn in transactions:
                if txn.get('type') == 'credit':
                    txn['category'] = 'income'
                else:
                    txn['category'] = 'other'
            return transactions

        # Map categories back to transactions
        category_map = {cat.index: cat.category.value for cat in parsed_result.categories}

        for i, txn in enumerate(transactions):
            if i in category_map:
                txn['category'] = category_map[i]
            else:
                # Fallback for missing categories
                txn['category'] = 'income' if txn.get('type') == 'credit' else 'other'

        logger.info(f"LLM categorization complete: {len(category_map)} categories assigned")
        return transactions

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Categorization error: {error_msg}", exc_info=True)

        # Fallback: assign default categories
        for txn in transactions:
            if txn.get('type') == 'credit':
                txn['category'] = 'income'
            else:
                txn['category'] = 'other'

        return transactions


async def process_financial_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process parsed financial data by adding categories via LLM.

    Args:
        parsed_data: Output from transaction_parser.parse_transactions()

    Returns:
        Complete financial data with categories
    """
    if not parsed_data.get('is_financial_statement'):
        return parsed_data

    transactions = parsed_data.get('transactions', [])

    # Categorize transactions using LLM
    categorized = await categorize_transactions(transactions)

    # Update parsed data with categorized transactions
    parsed_data['transactions'] = categorized

    return parsed_data


# Keep legacy function for backwards compatibility during transition
async def extract_financial_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function - kept for backward compatibility.
    Now uses hybrid approach: Python parsing + LLM categorization.
    """
    from services.transaction_parser import parse_transactions

    text_content = extracted_data.get('text', '')

    if not text_content:
        return {
            "is_financial_statement": False,
            "opening_balance": None,
            "closing_balance": None,
            "transactions": [],
            "error": "No text content provided"
        }

    # Parse transactions using Python
    parsed_data = parse_transactions(text_content)
    logger.info(f"Parsed {len(parsed_data.get('transactions', []))} transactions from text")

    if not parsed_data.get('is_financial_statement'):
        return {
            "is_financial_statement": False,
            "opening_balance": None,
            "closing_balance": None,
            "transactions": [],
            "error": "Could not parse as financial statement"
        }

    # Categorize using LLM
    result = await process_financial_data(parsed_data)

    return result
