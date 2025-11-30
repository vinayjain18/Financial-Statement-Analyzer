"""
LLM Processor Service
Uses OpenAI Structured Outputs with Pydantic for guaranteed JSON compliance.
GPT only extracts transactions and categorizes them - all calculations done by Python.
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI, LengthFinishReasonError
from dotenv import load_dotenv

from services.pdf_extractor import format_tables_for_prompt
from services.schemas import FinancialExtraction

load_dotenv()

# Setup logging
logger = logging.getLogger('llm_processor')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a financial document analyzer. Your job is to:
1. Determine if the document is a valid bank/financial statement
2. Extract opening and closing balance if available
3. Extract all transactions with date, description, amount, and type
4. Categorize each transaction into specific categories

Rules:
- is_financial_statement: Set to true ONLY if this is a bank statement, credit card statement, or financial transaction document. Set to false for invoices, receipts, resumes, or other documents.
- All amounts must be POSITIVE numbers

===== STEP 1: DETERMINE CREDIT VS DEBIT (MOST IMPORTANT) =====

The bank statement table has these columns:
Date | Narration | Ref No | Value Date | Withdrawal Amount | Deposit Amount | Closing Balance

CRITICAL: You MUST determine transaction type ONLY by looking at which column has the non-zero amount:
- If "Withdrawal Amount" column has a non-zero value → type = "debit" (money going OUT)
- If "Deposit Amount" column has a non-zero value → type = "credit" (money coming IN)

Example rows:
Row: "UPI-NEXTBILLION TECHNOLO-GROWW..." | 10,000.00 | 0.00 | 50,000.00
     → Withdrawal=10,000.00 (non-zero), Deposit=0.00 (zero) → This is DEBIT, amount=10000.00

Row: "NEFT-SALARY-COMPANY..." | 0.00 | 25,000.00 | 75,000.00
     → Withdrawal=0.00 (zero), Deposit=25,000.00 (non-zero) → This is CREDIT, amount=25000.00

WARNING: NEVER determine type based on description/narration. ONLY use the column values.
- "GROWW" in description does NOT mean it's income - check the Withdrawal/Deposit columns!
- "SALARY" in description does NOT automatically mean credit - check the columns!

===== STEP 2: CATEGORIZE AFTER DETERMINING TYPE =====

ONLY after you have determined the type from column values, assign a category:

For type="credit" (Deposit column had the amount) - USE ONLY:
- income: ALL incoming money (salary, NEFT, interest, refunds, transfers IN)
- dividend: ONLY if description explicitly contains "DIVIDEND"

For type="debit" (Withdrawal column had the amount) - USE:
- food: Groceries, DMart, BigBasket, restaurants, Zomato, Swiggy, "AVENUE SUPERMARTS"
- bills: Utilities, rent, mobile recharge, "JIO PREPAID", subscriptions, Claude.ai, "GOOGLE ONE"
- shopping: Amazon, Flipkart, online shopping, retail stores
- transport: Uber, Ola, Metro, "INDIAN RAILWAYS", fuel
- health: Hospitals, pharmacies, medical
- entertainment: Movies, Netflix, Prime, Spotify, gaming
- investment: Groww, Zerodha, mutual funds, stocks, "NEXTBILLION TECHNOLO"
- transfer: UPI transfers to individuals
- emi: EMI payments, loan repayments, "BAJAJ FINANCE"
- other: ONLY if nothing else fits

===== STRICT VALIDATION =====
1. Type determination: ALWAYS based on Withdrawal/Deposit column values, NEVER on description
2. If type="credit", category MUST be "income" or "dividend"
3. If type="debit", category must be one of: food, bills, shopping, transport, health, entertainment, investment, transfer, emi, other

Do NOT calculate totals - just extract individual transactions.
If you cannot find opening/closing balance, set them to null.
If this is not a financial statement, set is_financial_statement to false and return empty transactions list."""


async def extract_financial_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract financial data from PDF using GPT with Structured Outputs.
    Uses Pydantic model for guaranteed JSON compliance.

    Returns:
        Dict with is_financial_statement, opening_balance, closing_balance, transactions
    """
    logger.info("Starting GPT extraction with Structured Outputs")

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

    user_prompt = f"""Analyze this document and extract financial data.

DOCUMENT TEXT:
{text_content}

TABLES:
{tables_formatted}

Determine if this is a financial statement, extract balances and all transactions, and categorize each transaction."""

    try:
        logger.info("Making OpenAI API call with Structured Outputs")

        # Use beta.chat.completions.parse for structured output
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format=FinancialExtraction,
            temperature=0,
            max_tokens=4096
        )

        # Get the parsed result
        message = completion.choices[0].message
        finish_reason = completion.choices[0].finish_reason
        logger.info(f"Response received. finish_reason: {finish_reason}")

        # Check if model refused to respond
        if message.refusal:
            logger.warning(f"Model refused: {message.refusal}")
            return {
                "is_financial_statement": False,
                "opening_balance": None,
                "closing_balance": None,
                "transactions": [],
                "error": f"Model refused to process: {message.refusal}"
            }

        # Get parsed Pydantic object
        parsed_result: Optional[FinancialExtraction] = message.parsed

        if parsed_result is None:
            logger.error("Parsed result is None")
            return {
                "is_financial_statement": False,
                "opening_balance": None,
                "closing_balance": None,
                "transactions": [],
                "error": "Failed to parse response"
            }

        logger.info(f"Successfully parsed. is_financial_statement: {parsed_result.is_financial_statement}")
        logger.info(f"Transactions count: {len(parsed_result.transactions)}")

        # Convert Pydantic model to dict for downstream processing
        return {
            "is_financial_statement": parsed_result.is_financial_statement,
            "opening_balance": parsed_result.opening_balance,
            "closing_balance": parsed_result.closing_balance,
            "transactions": [
                {
                    "date": t.date,
                    "description": t.description,
                    "category": t.category.value,
                    "amount": t.amount,
                    "type": t.type.value
                }
                for t in parsed_result.transactions
            ]
        }

    except LengthFinishReasonError as e:
        # Response was cut off due to max_tokens
        logger.error(f"Response truncated (too long): {e}")
        return {
            "is_financial_statement": False,
            "opening_balance": None,
            "closing_balance": None,
            "transactions": [],
            "error": "Document too large to process. Please try a smaller statement."
        }
    except Exception as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        raise Exception(f"OpenAI API error: {str(e)}")
