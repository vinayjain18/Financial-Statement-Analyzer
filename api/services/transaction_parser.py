"""
Generic Transaction Parser Service
Parses bank statements from ANY bank using pattern auto-detection.
No bank-specific logic - uses universal patterns for dates, amounts, and balances.
Credit/Debit is determined by comparing consecutive closing balances.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger('transaction_parser')


@dataclass
class StatementSummary:
    """Summary extracted from the statement"""
    opening_balance: Optional[float]
    closing_balance: Optional[float]
    total_debits: Optional[float]
    total_credits: Optional[float]


# =============================================================================
# UNIVERSAL REGEX PATTERNS
# =============================================================================

# Universal date pattern - matches all common formats:
# DD/MM/YY, DD/MM/YYYY, DD-MM-YY, DD-MM-YYYY, DD.MM.YY, DD.MM.YYYY
# Also matches: 01-Nov-2025, 01 Nov 2025, etc.
DATE_PATTERN = re.compile(
    r'\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]\d{2,4})\b',
    re.IGNORECASE
)

# Universal amount pattern - matches:
# Indian format: 1,23,456.78 or 12,34,567.89
# Western format: 1,234,567.89
# Simple format: 1234.56
# With optional Cr/Dr suffix
AMOUNT_PATTERN = re.compile(
    r'(\d{1,3}(?:,\d{2,3})*\.\d{2}|\d+\.\d{2})\s*(Cr|Dr)?',
    re.IGNORECASE
)

# Pattern to detect if a line likely contains a transaction
# Must have at least one date-like pattern and one amount-like pattern
def is_potential_transaction_line(line: str) -> bool:
    """Check if line potentially contains transaction data"""
    stripped = line.strip()
    if not stripped or len(stripped) < 10:
        return False

    has_date = bool(DATE_PATTERN.search(stripped))
    has_amount = bool(AMOUNT_PATTERN.search(stripped))

    return has_date and has_amount


# =============================================================================
# AMOUNT PARSING
# =============================================================================

def parse_amount(amount_str: str) -> float:
    """
    Parse amount string to float.
    Handles Indian format (1,23,456.78) and Western format (1,234,567.89)
    """
    if not amount_str:
        return 0.0
    # Remove commas and whitespace
    cleaned = amount_str.replace(',', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_all_amounts(line: str) -> List[Tuple[float, Optional[str]]]:
    """
    Extract all amounts from a line with their Cr/Dr suffix if present.
    Returns list of (amount, suffix) tuples.
    """
    amounts = []
    for match in AMOUNT_PATTERN.finditer(line):
        amount = parse_amount(match.group(1))
        suffix = match.group(2).upper() if match.group(2) else None
        if amount > 0:  # Ignore zero amounts
            amounts.append((amount, suffix))
    return amounts


# =============================================================================
# DATE EXTRACTION
# =============================================================================

def extract_date(line: str) -> Optional[str]:
    """Extract the first date from a line"""
    match = DATE_PATTERN.search(line)
    return match.group(1) if match else None


def normalize_date(date_str: str) -> str:
    """Normalize date to consistent format DD/MM/YYYY"""
    if not date_str:
        return ""
    # Replace common separators with /
    normalized = re.sub(r'[-\.]', '/', date_str)
    return normalized


# =============================================================================
# SUMMARY EXTRACTION (Keyword-based)
# =============================================================================

def extract_statement_summary(text: str) -> Optional[StatementSummary]:
    """
    Extract opening/closing balance using keyword matching.
    Works with any bank format by looking for common keywords.
    """
    opening_balance = None
    closing_balance = None
    total_debits = None
    total_credits = None

    lines = text.split('\n')

    for i, line in enumerate(lines):
        lower_line = line.lower()

        # Look for total debits FIRST (before opening balance to avoid confusion)
        if total_debits is None and 'total' in lower_line and 'debit' in lower_line:
            amounts = extract_all_amounts(line)
            if amounts:
                total_debits = amounts[0][0]
                # If opening balance is on same line, it's the second amount
                if opening_balance is None and 'opening' in lower_line and len(amounts) >= 2:
                    opening_balance = amounts[1][0]

        # Look for total credits
        if total_credits is None and 'total' in lower_line and 'credit' in lower_line:
            amounts = extract_all_amounts(line)
            if amounts:
                total_credits = amounts[0][0]
                # If closing balance is on same line, it's the second amount
                if closing_balance is None and 'closing' in lower_line and len(amounts) >= 2:
                    closing_balance = amounts[1][0]

        # Look for opening balance (only if not already found)
        if opening_balance is None and 'opening' in lower_line and 'balance' in lower_line:
            # Skip if this line also has "total debit" (already handled above)
            if 'total' not in lower_line:
                amounts = extract_all_amounts(line)
                if amounts:
                    opening_balance = amounts[-1][0]  # Usually last amount on the line
                elif i + 1 < len(lines):
                    amounts = extract_all_amounts(lines[i + 1])
                    if amounts:
                        opening_balance = amounts[0][0]

        # Look for closing balance (only if not already found)
        if closing_balance is None and 'closing' in lower_line and 'balance' in lower_line:
            # Skip if this line also has "total credit" (already handled above)
            if 'total' not in lower_line:
                amounts = extract_all_amounts(line)
                if amounts:
                    closing_balance = amounts[-1][0]  # Usually last amount
                elif i + 1 < len(lines):
                    amounts = extract_all_amounts(lines[i + 1])
                    if amounts:
                        closing_balance = amounts[-1][0]

    # Try alternative patterns if not found
    # Pattern: "Opening Balance : 2,89,846.56 Cr" on same line
    if opening_balance is None:
        match = re.search(r'opening\s*balance\s*[:\-]?\s*(\d{1,3}(?:,\d{2,3})*\.\d{2})', text, re.IGNORECASE)
        if match:
            opening_balance = parse_amount(match.group(1))

    if closing_balance is None:
        match = re.search(r'closing\s*balance\s*[:\-]?\s*(\d{1,3}(?:,\d{2,3})*\.\d{2})', text, re.IGNORECASE)
        if match:
            closing_balance = parse_amount(match.group(1))

    # HDFC-style summary: 6 numbers in a row
    # Pattern supports both Indian format (1,23,456.78) and Western format (1,234,567.89)
    amount_regex = r'(\d{1,3}(?:,\d{2,3})*\.\d{2})'
    hdfc_pattern = re.compile(
        amount_regex + r'\s+'  # Opening balance
        r'(\d+)\s+'            # Dr count
        r'(\d+)\s+'            # Cr count
        + amount_regex + r'\s+'  # Total debits
        + amount_regex + r'\s+'  # Total credits
        + amount_regex           # Closing balance
    )
    match = hdfc_pattern.search(text)
    if match:
        if opening_balance is None:
            opening_balance = parse_amount(match.group(1))
        if total_debits is None:
            total_debits = parse_amount(match.group(4))
        if total_credits is None:
            total_credits = parse_amount(match.group(5))
        if closing_balance is None:
            closing_balance = parse_amount(match.group(6))

    if opening_balance is not None or closing_balance is not None:
        return StatementSummary(
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            total_debits=total_debits,
            total_credits=total_credits
        )

    return None


# =============================================================================
# TRANSACTION LINE DETECTION
# =============================================================================

def is_header_or_footer(line: str) -> bool:
    """Check if line is a header, footer, or non-transaction content"""
    stripped = line.strip().lower()
    if not stripped:
        return True

    # Always skip these patterns - account header info that may contain dates/amounts
    always_skip_patterns = [
        'a/c open date', 'open date', 'expected amb', 'joint holders',
        'account status', 'account number', 'cust id', 'pr.code', 'br.code',
        'od limit', 'limit :', 'currency :', 'account open', 'not applicable'
    ]
    for pattern in always_skip_patterns:
        if pattern in stripped:
            return True

    # Skip patterns - common headers/footers across banks
    skip_keywords = [
        'page', 'account', 'a/c', 'branch', 'address', 'city', 'state', 'phone',
        'email', 'ifsc', 'micr', 'nomination', 'customer', 'statement',
        'generated', 'registered', 'disclaimer', 'contents', 'gstin',
        'linked', 'deposits', 'loan', 'locker', 'facility', 'scheme',
        'no records', 'si ', 'sl ', 'particulars', 'narration', 'chq',
        'withdrawal', 'deposit', 'balance', 'date', 'ref', 'details of',
        'name &', 'summary', 'total', 'opening', 'closing', 'end of'
    ]

    # Check if line starts with or contains skip keywords
    for keyword in skip_keywords:
        if stripped.startswith(keyword) or (keyword in stripped and len(stripped) < 50):
            # But don't skip if it has amounts (could be summary with data)
            if not AMOUNT_PATTERN.search(line) or 'total' in stripped or 'balance' in stripped:
                return True

    # Skip lines that are just numbers (page numbers, serial numbers alone)
    if re.match(r'^\d+\s*(of\s*\d+)?$', stripped):
        return True

    # Skip lines that are just special characters
    if re.match(r'^[=\-_*#]+$', stripped):
        return True

    return False


def find_transaction_lines(text: str) -> List[Tuple[int, str]]:
    """
    Find all lines that contain transaction data.
    Returns list of (line_index, line_text) tuples.

    A transaction line must have:
    1. A date pattern
    2. At least one amount
    3. Not be a header/footer
    """
    lines = text.split('\n')
    transaction_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Skip headers/footers
        if is_header_or_footer(stripped):
            continue

        # Check for transaction pattern
        if is_potential_transaction_line(stripped):
            transaction_lines.append((i, stripped))

    return transaction_lines


# =============================================================================
# TRANSACTION PARSING
# =============================================================================

def parse_transaction_line(line: str, prev_line: str = "", next_line: str = "") -> Optional[Dict[str, Any]]:
    """
    Parse a single transaction line.

    Handles multiple formats:
    1. Date at start: "28/06/2025 Description 100.00 5000.00"
    2. Serial + Date: "1 01-11-2025 Description 100.00 5000.00 Cr"
    3. Description before: prev_line has description, current has date+amounts

    Returns dict with: date, description, amount, closing_balance, type
    """
    stripped = line.strip()
    if not stripped:
        return None

    # Extract date
    date = extract_date(stripped)
    if not date:
        return None

    # Extract all amounts with Cr/Dr suffix
    amounts = extract_all_amounts(stripped)
    if not amounts:
        return None

    # Last amount is typically the closing balance
    closing_balance = amounts[-1][0]
    closing_suffix = amounts[-1][1]  # Cr or Dr

    # Transaction amount is second-to-last (if exists) or calculated later
    transaction_amount = None
    if len(amounts) >= 2:
        transaction_amount = amounts[-2][0]

    # Determine transaction type from Cr/Dr suffix or column position
    txn_type = 'unknown'
    if closing_suffix:
        # Some statements put Cr/Dr on balance, not on transaction
        pass

    # If we have 3+ amounts: [withdrawal, deposit, balance] - HDFC style
    if len(amounts) >= 3:
        withdrawal = amounts[-3][0]
        deposit = amounts[-2][0]
        if withdrawal > 0 and deposit == 0:
            txn_type = 'debit'
            transaction_amount = withdrawal
        elif deposit > 0 and withdrawal == 0:
            txn_type = 'credit'
            transaction_amount = deposit

    # If we have 2 amounts: [amount, balance] - need to check Cr/Dr or position
    elif len(amounts) == 2:
        amt_suffix = amounts[0][1]
        if amt_suffix:
            txn_type = 'credit' if amt_suffix == 'CR' else 'debit'
        transaction_amount = amounts[0][0]

    # Extract description - remove date and amounts from the line
    description = stripped

    # Remove the date
    description = DATE_PATTERN.sub('', description)

    # Remove amounts and Cr/Dr
    description = AMOUNT_PATTERN.sub('', description)

    # Remove serial numbers at start (like "1 ", "12 ", etc.)
    description = re.sub(r'^\d+\s+', '', description)

    # Clean up description
    description = ' '.join(description.split())

    # If description is empty or too short, use prev_line as description
    if len(description) < 3 and prev_line:
        prev_stripped = prev_line.strip()
        if not is_header_or_footer(prev_stripped) and not is_potential_transaction_line(prev_stripped):
            description = prev_stripped + ' ' + description

    return {
        'date': normalize_date(date),
        'description': description.strip(),
        'amount': transaction_amount,
        'closing_balance': closing_balance,
        'type': txn_type
    }


def determine_transaction_type(current_balance: float, previous_balance: float) -> str:
    """
    Determine if transaction is credit or debit by comparing balances.
    - If balance increased → credit (money came in)
    - If balance decreased → debit (money went out)
    """
    if current_balance > previous_balance:
        return 'credit'
    elif current_balance < previous_balance:
        return 'debit'
    return 'unknown'


# =============================================================================
# MAIN PARSING FUNCTION
# =============================================================================

def parse_transactions(text: str) -> Dict[str, Any]:
    """
    Parse all transactions from bank statement text.
    Works with ANY bank format using pattern auto-detection.

    Returns:
        Dict with:
        - is_financial_statement: bool
        - opening_balance: float
        - closing_balance: float
        - transactions: List of transaction dicts
    """
    # Extract statement summary
    summary = extract_statement_summary(text)

    # Find all transaction lines
    transaction_lines = find_transaction_lines(text)

    if not transaction_lines:
        # Try alternative: look for lines with amounts and dates more aggressively
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if DATE_PATTERN.search(line) and AMOUNT_PATTERN.search(line):
                transaction_lines.append((i, line.strip()))

    # Step 3: Parse each transaction line
    lines = text.split('\n')
    raw_transactions = []
    pending_description = None

    for idx, (line_num, line) in enumerate(transaction_lines):
        # Get previous and next lines for context
        prev_line = lines[line_num - 1] if line_num > 0 else ""
        next_line = lines[line_num + 1] if line_num < len(lines) - 1 else ""

        # Check if previous line might be a description prefix
        if pending_description:
            prev_line = pending_description
            pending_description = None

        parsed = parse_transaction_line(line, prev_line, next_line)
        if parsed:
            raw_transactions.append(parsed)

        # Check if next line is a description continuation (no date, no amounts)
        if next_line and not is_potential_transaction_line(next_line) and not is_header_or_footer(next_line):
            if raw_transactions:
                raw_transactions[-1]['description'] += ' ' + next_line.strip()

    # Determine credit/debit for each transaction using balance comparison
    transactions = []
    previous_balance = summary.opening_balance if summary else None

    for i, txn in enumerate(raw_transactions):
        current_balance = txn['closing_balance']

        # Use parsed type if available, otherwise determine from balance
        txn_type = txn.get('type', 'unknown')

        if txn_type == 'unknown' and previous_balance is not None:
            txn_type = determine_transaction_type(current_balance, previous_balance)

        # Calculate amount from balance difference if not extracted
        if txn['amount'] is None and previous_balance is not None:
            txn['amount'] = abs(current_balance - previous_balance)

        transactions.append({
            'date': txn['date'],
            'description': txn['description'].strip(),
            'reference': '',  # Will be extracted if needed
            'amount': txn['amount'] or 0.0,
            'closing_balance': current_balance,
            'type': txn_type,
            'category': None  # To be filled by LLM
        })

        previous_balance = current_balance

    # Determine if this is a valid financial statement
    is_financial = len(transactions) > 0

    # Use last transaction's closing balance as the statement's closing balance
    # This is more reliable than parsing from summary section
    last_txn_closing = transactions[-1]['closing_balance'] if transactions else None

    return {
        'is_financial_statement': is_financial,
        'opening_balance': summary.opening_balance if summary else None,
        'closing_balance': last_txn_closing if last_txn_closing is not None else summary.closing_balance if summary else None,
        'total_debits': summary.total_debits if summary else None,
        'total_credits': summary.total_credits if summary else None,
        'transactions': transactions
    }


def get_unique_descriptions(transactions: List[Dict]) -> List[str]:
    """
    Get list of unique descriptions for LLM categorization.
    """
    descriptions = set()

    for txn in transactions:
        desc = txn.get('description', '')
        # Clean and extract key part
        cleaned = re.sub(r'^(UPI[-/]?|NEFT[-/]?|IMPS[-/]?|POS\s*|ATM\s*|ACH\s*|RTGS[-/]?)', '', desc, flags=re.IGNORECASE)
        # Take first meaningful part
        parts = cleaned.split('/')[0].split('@')[0].strip()
        if parts and len(parts) > 2:
            descriptions.add(parts[:50])

    return list(descriptions)
