"""
Calculator Service
All financial calculations are done in Python for 100% accuracy.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger('calculator')


def calculate_financials(gpt_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all financial totals from GPT-extracted data.

    Args:
        gpt_response: Dict containing is_financial_statement, opening_balance,
                      closing_balance, and transactions from GPT

    Returns:
        Complete financial summary with calculated totals
    """
    logger.info("Starting financial calculations")

    # Check if valid financial statement (handle both snake_case and camelCase)
    is_financial = gpt_response.get("is_financial_statement", gpt_response.get("isFinancialStatement", False))

    if not is_financial:
        logger.warning("Document is not a financial statement")
        return {
            "success": False,
            "error": "The uploaded document is not a valid bank statement. Please upload a bank statement PDF."
        }

    # Check for GPT errors
    if "error" in gpt_response:
        logger.error(f"GPT returned error: {gpt_response['error']}")
        return {
            "success": False,
            "error": gpt_response["error"]
        }

    transactions = gpt_response.get("transactions", [])
    logger.info(f"Processing {len(transactions)} transactions")

    # Handle empty transactions
    if not transactions:
        logger.warning("No transactions found in the document")
        # Still return success but with zero values
        opening_balance = gpt_response.get("opening_balance", gpt_response.get("openingBalance"))
        closing_balance = gpt_response.get("closing_balance", gpt_response.get("closingBalance"))

        return {
            "success": True,
            "openingBalance": float(opening_balance) if opening_balance is not None else 0,
            "closingBalance": float(closing_balance) if closing_balance is not None else 0,
            "totalIncome": 0,
            "totalExpenses": 0,
            "netChange": 0,
            "transactions": [],
            "categoryBreakdown": {},
            "transactionCount": 0
        }

    # Calculate totals
    total_income = 0.0
    total_expenses = 0.0
    category_breakdown = {}  # For expenses
    income_breakdown = {}  # For income

    for txn in transactions:
        try:
            amount = abs(float(txn.get("amount", 0)))
            txn_type = txn.get("type", "debit").lower()
            category = txn.get("category", "other").lower()

            if txn_type == "credit":
                total_income += amount
                # Add to income breakdown
                if category not in income_breakdown:
                    income_breakdown[category] = 0.0
                income_breakdown[category] += amount
            else:
                total_expenses += amount
                # Add to category breakdown (expenses)
                if category not in category_breakdown:
                    category_breakdown[category] = 0.0
                category_breakdown[category] += amount

        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid transaction data: {txn}, error: {e}")
            continue

    # Round all values
    total_income = round(total_income, 2)
    total_expenses = round(total_expenses, 2)
    category_breakdown = {k: round(v, 2) for k, v in category_breakdown.items()}
    income_breakdown = {k: round(v, 2) for k, v in income_breakdown.items()}

    # Sort breakdowns by amount (highest first)
    category_breakdown = dict(
        sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
    )
    income_breakdown = dict(
        sorted(income_breakdown.items(), key=lambda x: x[1], reverse=True)
    )

    # Get opening and closing balance (handle both snake_case and camelCase)
    opening_balance = gpt_response.get("opening_balance", gpt_response.get("openingBalance"))
    closing_balance = gpt_response.get("closing_balance", gpt_response.get("closingBalance"))

    # Convert to float if not None
    if opening_balance is not None:
        try:
            opening_balance = round(float(opening_balance), 2)
        except (ValueError, TypeError):
            opening_balance = None

    if closing_balance is not None:
        try:
            closing_balance = round(float(closing_balance), 2)
        except (ValueError, TypeError):
            closing_balance = None

    # If we have opening balance but no closing, calculate it
    if opening_balance is not None and closing_balance is None:
        closing_balance = round(opening_balance + total_income - total_expenses, 2)
        logger.info(f"Calculated closing balance: {closing_balance}")

    # Build final result
    result = {
        "success": True,
        "openingBalance": opening_balance if opening_balance is not None else 0,
        "closingBalance": closing_balance if closing_balance is not None else 0,
        "totalIncome": total_income,
        "totalExpenses": total_expenses,
        "netChange": round(total_income - total_expenses, 2),
        "transactions": transactions,
        "categoryBreakdown": category_breakdown,
        "incomeBreakdown": income_breakdown,
        "transactionCount": len(transactions)
    }

    logger.info(f"Calculations complete - Income: {total_income}, Expenses: {total_expenses}")
    logger.info(f"Expense Categories: {list(category_breakdown.keys())}")
    logger.info(f"Income Categories: {list(income_breakdown.keys())}")

    return result


def get_summary_stats(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get additional summary statistics from the calculated result.
    """
    if not result.get("success"):
        return result

    transactions = result.get("transactions", [])

    # Count by type
    credit_count = sum(1 for t in transactions if t.get("type", "").lower() == "credit")
    debit_count = sum(1 for t in transactions if t.get("type", "").lower() == "debit")

    # Find largest transactions
    credits = [t for t in transactions if t.get("type", "").lower() == "credit"]
    debits = [t for t in transactions if t.get("type", "").lower() == "debit"]

    largest_credit = max(credits, key=lambda x: float(x.get("amount", 0)), default=None)
    largest_debit = max(debits, key=lambda x: float(x.get("amount", 0)), default=None)

    result["stats"] = {
        "creditCount": credit_count,
        "debitCount": debit_count,
        "largestCredit": largest_credit,
        "largestDebit": largest_debit
    }

    return result
