import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import tempfile
import os

from services.pdf_extractor import extract_pdf_data
from services.llm_processor import analyze_financial_data

# Setup logging - both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finsight.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('finsight_api')

app = FastAPI(title="FinSight API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/python/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "message": "FinSight API is running"}


@app.post("/api/python/analyze")
async def analyze_statement(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze a bank statement PDF and return financial insights.
    """
    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

    # Validate file type
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read and check file size
    content = await file.read()
    file_size = len(content)
    logger.info(f"File size: {file_size} bytes")

    if file_size > 10 * 1024 * 1024:
        logger.warning(f"File too large: {file_size} bytes")
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    try:
        # Save to temp file for processing
        logger.info("Saving to temporary file")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        logger.info(f"Temp file created: {tmp_path}")

        # Extract data from PDF
        logger.info("Starting PDF extraction")
        extracted_data = extract_pdf_data(tmp_path)

        text_length = len(extracted_data.get("text", ""))
        tables_count = len(extracted_data.get("tables", []))
        logger.info(f"Extraction complete. Text: {text_length} chars, Tables: {tables_count}")

        if not extracted_data["text"] and not extracted_data["tables"]:
            logger.error("No data extracted from PDF")
            raise HTTPException(
                status_code=400,
                detail="Could not extract data from PDF. Please ensure it's a valid bank statement."
            )

        # Analyze with LLM
        logger.info("Starting LLM analysis")
        analysis = await analyze_financial_data(extracted_data)
        logger.info("LLM analysis complete")

        return {
            "success": True,
            "data": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temp file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            logger.info(f"Temp file deleted: {tmp_path}")


# Required for Vercel
handler = app
