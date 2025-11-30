"""
LLM Processor Service
Uses OpenAI for financial analysis with structured output.
"""

import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from services.pdf_extractor import format_tables_for_prompt

load_dotenv()

# Setup logging - both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finsight.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('llm_processor')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a financial analyst. Analyze the bank statement and extract all financial data.

Your task:
1. Find the opening and closing balance
2. Extract ALL transactions with date, description, amount, and type (credit/debit)
3. Categorize each transaction into ONE of: groceries, utilities, entertainment, dining, transportation, income, healthcare, shopping, transfers, or other
4. Calculate totals for income (sum of all credits) and expenses (sum of all debits)
5. Calculate the total for each category

IMPORTANT: Return ONLY a valid JSON object with this exact structure (no markdown, no explanation):
{
    "openingBalance": number,
    "closingBalance": number,
    "totalIncome": number,
    "totalExpenses": number,
    "transactions": [
        {
            "date": "YYYY-MM-DD or original date format",
            "description": "transaction description",
            "category": "category name",
            "amount": positive number,
            "type": "credit" or "debit"
        }
    ],
    "categoryBreakdown": {
        "category_name": total_amount_for_that_category
    }
}

Rules:
- All amounts must be positive numbers
- "credit" = money coming in (income, deposits, refunds)
- "debit" = money going out (expenses, purchases, payments)
- categoryBreakdown should only include categories that have transactions
- Be accurate with the math - double check your totals"""


async def analyze_financial_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze extracted PDF data using OpenAI.
    Simple approach without tool calling for reliability.
    """
    logger.info("Starting financial data analysis")

    # Format the prompt - limit text to avoid token limits
    text_content = extracted_data.get('text', '')
    original_length = len(text_content)
    if len(text_content) > 15000:
        text_content = text_content[:15000] + "\n...[truncated]"
    logger.info(f"Text content length: {original_length}, after truncation: {len(text_content)}")

    tables_formatted = format_tables_for_prompt(extracted_data.get("tables", []))
    if len(tables_formatted) > 5000:
        tables_formatted = tables_formatted[:5000] + "\n...[truncated]"
    logger.info(f"Tables formatted length: {len(tables_formatted)}")

    user_prompt = f"""Analyze this bank statement and extract all financial data.

STATEMENT TEXT:
{text_content}

TABLES:
{tables_formatted}

Extract all transactions, categorize them, calculate totals, and return the JSON response."""

    try:
        logger.info("Making OpenAI API call")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            max_tokens=4096
        )

        content = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        logger.info(f"Response received. finish_reason: {finish_reason}, content length: {len(content) if content else 0}")

        if not content:
            logger.error("Empty response from OpenAI")
            return create_error_response("Empty response from AI")

        # Clean and parse JSON
        content = content.strip()

        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]

        content = content.strip()
        logger.info(f"Cleaned content length: {len(content)}")
        logger.debug(f"Content preview: {content[:200]}...")

        result = json.loads(content)
        logger.info("Successfully parsed JSON response")

        # Validate and fix the result
        result = validate_and_fix_result(result)

        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Raw content: {content[:1000] if 'content' in locals() and content else 'N/A'}")
        return create_error_response(f"Failed to parse AI response as JSON")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        raise Exception(f"OpenAI API error: {str(e)}")


def validate_and_fix_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix the result structure."""
    logger.info("Validating result structure")

    # Ensure all required fields exist
    defaults = {
        "openingBalance": 0,
        "closingBalance": 0,
        "totalIncome": 0,
        "totalExpenses": 0,
        "transactions": [],
        "categoryBreakdown": {}
    }

    for key, default_value in defaults.items():
        if key not in result:
            logger.warning(f"Missing field '{key}', using default")
            result[key] = default_value

    # Recalculate totals from transactions if they exist
    if result["transactions"]:
        total_income = 0
        total_expenses = 0
        category_totals = {}

        for txn in result["transactions"]:
            amount = abs(float(txn.get("amount", 0)))
            txn_type = txn.get("type", "debit")
            category = txn.get("category", "other")

            if txn_type == "credit":
                total_income += amount
            else:
                total_expenses += amount
                # Only count expenses in category breakdown
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount

        # Update with recalculated values
        result["totalIncome"] = round(total_income, 2)
        result["totalExpenses"] = round(total_expenses, 2)
        result["categoryBreakdown"] = {k: round(v, 2) for k, v in category_totals.items()}

        logger.info(f"Recalculated - Income: {result['totalIncome']}, Expenses: {result['totalExpenses']}")
        logger.info(f"Category breakdown: {result['categoryBreakdown']}")

    return result


def create_error_response(error_msg: str) -> Dict[str, Any]:
    """Create a standard error response."""
    return {
        "openingBalance": 0,
        "closingBalance": 0,
        "totalIncome": 0,
        "totalExpenses": 0,
        "transactions": [],
        "categoryBreakdown": {},
        "error": error_msg
    }
