import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import tempfile
import os
import sys
import httpx

# Rate limiting imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# hCaptcha configuration
HCAPTCHA_SECRET_KEY = os.getenv("HCAPTCHA_SECRET_KEY")
HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"

# Add the current directory to sys.path for Vercel deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from services.pdf_extractor import extract_pdf_data
from services.llm_processor import extract_financial_data
from services.calculator import calculate_financials

# Setup logging - console only (file logging not available on serverless)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('finsight_api')

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="FinSight API", version="1.0.0")

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration - restricted to specific origins
ALLOWED_ORIGINS = [
    "https://financial-statement-analyzer-three.vercel.app",
    "http://localhost:3000",  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


async def verify_hcaptcha(token: str, remote_ip: str) -> bool:
    """Verify hCaptcha token with hCaptcha API"""
    if not HCAPTCHA_SECRET_KEY:
        logger.warning("HCAPTCHA_SECRET_KEY not configured, skipping verification")
        return True  # Skip verification if not configured (for development)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                HCAPTCHA_VERIFY_URL,
                data={
                    "secret": HCAPTCHA_SECRET_KEY,
                    "response": token,
                    "remoteip": remote_ip
                }
            )
            result = response.json()
            return result.get("success", False)
    except Exception as e:
        logger.error(f"hCaptcha verification error: {str(e)}")
        return False


@app.get("/api/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "message": "FinSight API is running"}


@app.post("/api/analyze")
@limiter.limit("10/hour")  # Rate limit: 10 uploads per hour per IP
async def analyze_statement(
    request: Request,
    file: UploadFile = File(...),
    hcaptcha_token: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Analyze a bank statement PDF and return financial insights.

    Flow:
    1. Verify hCaptcha token (if configured)
    2. Extract text/tables from PDF (pdfplumber)
    3. Send to GPT for extraction and categorization
    4. Validate if it's a financial statement
    5. Calculate totals using Python
    6. Return complete financial summary
    """
    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

    # Verify hCaptcha token
    if HCAPTCHA_SECRET_KEY:
        if not hcaptcha_token:
            logger.warning("hCaptcha token missing")
            raise HTTPException(status_code=400, detail="Please complete the captcha verification")

        client_ip = request.client.host if request.client else "unknown"
        is_valid = await verify_hcaptcha(hcaptcha_token, client_ip)
        if not is_valid:
            logger.warning("hCaptcha verification failed")
            raise HTTPException(status_code=400, detail="Captcha verification failed. Please try again.")

    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Validate content type
    if file.content_type != "application/pdf":
        logger.warning(f"Invalid content type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed")

    # Read and check file size
    content = await file.read()
    file_size = len(content)
    logger.info(f"File size: {file_size} bytes")

    if file_size > 10 * 1024 * 1024:
        logger.warning(f"File too large: {file_size} bytes")
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    # PDF magic byte validation - check for %PDF header
    if not content.startswith(b'%PDF'):
        logger.warning("Invalid PDF: Missing PDF magic bytes")
        raise HTTPException(status_code=400, detail="Invalid PDF file format")

    tmp_path = None
    try:
        # Step 1: Save to temp file for processing
        logger.info("Step 1: Saving to temporary file")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        logger.info(f"Temp file created: {tmp_path}")

        # Step 2: Extract data from PDF
        logger.info("Step 2: Extracting data from PDF")
        extracted_data = extract_pdf_data(tmp_path)

        text_length = len(extracted_data.get("text", ""))
        tables_count = len(extracted_data.get("tables", []))
        logger.info(f"Extraction complete. Text: {text_length} chars, Tables: {tables_count}")

        if not extracted_data["text"] and not extracted_data["tables"]:
            logger.error("No data extracted from PDF")
            raise HTTPException(
                status_code=400,
                detail="Could not extract data from PDF. Please ensure the file is not corrupted."
            )

        # Step 3: Send to GPT for extraction and categorization
        logger.info("Step 3: Sending to GPT for extraction and categorization")
        gpt_response = await extract_financial_data(extracted_data)

        # Step 4: Check if valid financial statement
        logger.info("Step 4: Validating document type")
        if not gpt_response.get("is_financial_statement", False):
            logger.warning("Document is not a financial statement")
            return {
                "success": False,
                "error": "The uploaded document is not a valid bank statement. Please upload a bank statement PDF.",
                "data": None
            }

        # Step 5: Calculate totals using Python
        logger.info("Step 5: Calculating financial totals")
        result = calculate_financials(gpt_response)

        if not result.get("success"):
            logger.error(f"Calculation failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error", "Failed to process financial data"),
                "data": None
            }

        logger.info("Analysis complete successfully")
        return {
            "success": True,
            "error": None,
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            logger.info(f"Temp file deleted: {tmp_path}")
