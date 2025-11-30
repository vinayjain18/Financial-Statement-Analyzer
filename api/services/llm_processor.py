"""
LLM Processor Service
Uses OpenAI with function calling for accurate financial calculations.
"""

import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

from services.pdf_extractor import format_tables_for_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Calculator tools for accurate math
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform basic math operations. Use this for ALL calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The operation to perform"
                    },
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["operation", "a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sum_list",
            "description": "Sum a list of numbers. Use this for totaling transactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to sum"
                    }
                },
                "required": ["numbers"]
            }
        }
    }
]


def calculate(operation: str, a: float, b: float) -> float:
    """Perform basic math operations."""
    ops = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else 0
    }
    return ops[operation](a, b)


def sum_list(numbers: List[float]) -> float:
    """Sum a list of numbers."""
    return sum(numbers)


def execute_tool(name: str, args: Dict) -> Any:
    """Execute a tool function by name."""
    if name == "calculate":
        return calculate(args["operation"], args["a"], args["b"])
    elif name == "sum_list":
        return sum_list(args["numbers"])
    return None


SYSTEM_PROMPT = """You are a financial analyst. Analyze the bank statement and extract:

1. Opening balance
2. Closing balance
3. All transactions with: date, description, amount, type (credit/debit)
4. Categorize each transaction (groceries, utilities, entertainment, dining, transportation, income, other)
5. Calculate total income and total expenses

IMPORTANT: Use the provided calculator tools for ALL math operations. Never calculate manually.

Return your analysis as valid JSON with this exact structure:
{
    "openingBalance": number,
    "closingBalance": number,
    "totalIncome": number,
    "totalExpenses": number,
    "transactions": [
        {
            "date": "YYYY-MM-DD",
            "description": "string",
            "category": "string",
            "amount": number (positive),
            "type": "credit" or "debit"
        }
    ],
    "categoryBreakdown": {
        "category_name": number (total amount)
    }
}"""


async def analyze_financial_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze extracted PDF data using OpenAI.

    Args:
        extracted_data: Dict with 'text' and 'tables' from PDF extraction

    Returns:
        Structured financial analysis
    """
    # Format the prompt
    tables_formatted = format_tables_for_prompt(extracted_data.get("tables", []))

    user_prompt = f"""Analyze this bank statement:

TEXT CONTENT:
{extracted_data.get('text', 'No text extracted')}

TABLES:
{tables_formatted}

Extract all financial data and return as JSON."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    # Call OpenAI with tools
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0
    )

    # Handle tool calls if any
    message = response.choices[0].message

    while message.tool_calls:
        # Execute each tool call
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = execute_tool(tool_call.function.name, args)

            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        # Get next response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0
        )
        message = response.choices[0].message

    # Parse the final response
    content = message.content

    # Extract JSON from response
    try:
        # Try to find JSON in the response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content

        return json.loads(json_str.strip())
    except json.JSONDecodeError:
        # Return a basic structure if parsing fails
        return {
            "openingBalance": 0,
            "closingBalance": 0,
            "totalIncome": 0,
            "totalExpenses": 0,
            "transactions": [],
            "categoryBreakdown": {},
            "error": "Could not parse financial data. Raw response available.",
            "rawResponse": content
        }
