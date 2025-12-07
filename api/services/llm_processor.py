"""
LLM Processor Service
Uses OpenAI Responses API with Pydantic for guaranteed JSON compliance.
GPT only extracts transactions and categorizes them - all calculations done by Python.
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

from services.schemas import FinancialExtraction

load_dotenv()

# Setup logging
logger = logging.getLogger('llm_processor')

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a financial document analyzer. Your job is to:
1. Determine if the document is a valid bank/financial statement
2. Extract opening and closing balance if available
3. Extract all transactions with date, description, amount, and type
4. Categorize each transaction into specific categories

Rules:
- is_financial_statement: Set to true ONLY if this is a bank statement, credit card statement, or financial transaction document. Set to false for invoices, receipts, resumes, or other documents.
- All amounts must be POSITIVE numbers

===== STEP 1: DETERMINE CREDIT VS DEBIT (MOST IMPORTANT) =====

The bank statement text shows transactions in this format:
Date | Narration | Ref No | Value Date | Withdrawal Amount | Deposit Amount | Closing Balance

CRITICAL: You MUST determine transaction type by analyzing the amounts shown:
- If a withdrawal amount is shown (money going OUT) → type = "debit"
- If a deposit amount is shown (money coming IN) → type = "credit"

Example transaction lines:
"02/09/25 MEDCSI435584XXXXXX8876CLAUDE.AISUBS 0000524512139693 02/09/25 2,085.06 261,976.06"
     → Has withdrawal amount 2,085.06 → This is DEBIT

"06/09/25 NEFTCR-IDIB000K086-CLIMATEFORCE... 28,000.00 288,180.63"
     → Has deposit amount 28,000.00 (balance increased) → This is CREDIT

TIP: Compare closing balances between transactions:
- If closing balance DECREASED → it was a DEBIT (withdrawal)
- If closing balance INCREASED → it was a CREDIT (deposit)

WARNING: NEVER determine type based on description/narration alone.
- "GROWW" in description does NOT mean it's income - check if balance decreased (debit) or increased (credit)!
- "SALARY" in description does NOT automatically mean credit - verify by balance change!

===== STEP 2: CATEGORIZE AFTER DETERMINING TYPE =====

ONLY after you have determined the type, assign a category:

For type="credit" (money coming IN) - USE ONLY:
- income: ALL incoming money (salary, NEFT, interest, refunds, transfers IN)
- dividend: ONLY if description explicitly contains "DIVIDEND"

For type="debit" (money going OUT) - USE:
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
1. Type determination: ALWAYS based on balance change (increased=credit, decreased=debit)
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

    # Get text content - no truncation, pass full data to LLM
    text_content = extracted_data.get('text', '')
    logger.info(f"Text content length: {len(text_content)}")

    user_prompt = f"""Analyze this bank statement and extract financial data.

DOCUMENT TEXT:
{text_content}

Determine if this is a financial statement, extract opening and closing balances, extract all transactions, and categorize each transaction."""

    try:
        logger.info("Making OpenAI API call with Responses API (gpt-5-mini)")

        # Use responses.parse for structured output with GPT-5-mini
        # Responses API uses: input (messages), text_format (Pydantic model)
        response = await client.responses.parse(
            model="gpt-5-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            text_format=FinancialExtraction
        )

        logger.info(f"Response received. Status: {response.status}")
        logger.info(f"Response object type: {type(response)}")
        logger.info(f"Full response: {response}")

        # Get parsed Pydantic object from output_parsed
        logger.info("Extracting output_parsed from response...")
        parsed_result: Optional[FinancialExtraction] = response.output_parsed
        logger.info(f"Parsed result type: {type(parsed_result)}")
        logger.info(f"Parsed result: {parsed_result}")

        if parsed_result is None:
            logger.error("Parsed result is None")
            # Check if there was a refusal
            if hasattr(response, 'refusal') and response.refusal:
                logger.warning(f"Model refused: {response.refusal}")
                return {
                    "is_financial_statement": False,
                    "opening_balance": None,
                    "closing_balance": None,
                    "transactions": [],
                    "error": f"Model refused to process: {response.refusal}"
                }
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

    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI API error: {error_msg}", exc_info=True)

        # Check for token limit errors
        if "length" in error_msg.lower() or "token" in error_msg.lower():
            return {
                "is_financial_statement": False,
                "opening_balance": None,
                "closing_balance": None,
                "transactions": [],
                "error": "Document too large to process. Please try a smaller statement."
            }

        raise Exception(f"OpenAI API error: {error_msg}")
