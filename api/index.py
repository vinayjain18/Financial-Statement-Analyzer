from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import tempfile
import os

from services.pdf_extractor import extract_pdf_data
from services.llm_processor import analyze_financial_data

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
    return {"status": "healthy", "message": "FinSight API is running"}


@app.post("/api/python/analyze")
async def analyze_statement(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze a bank statement PDF and return financial insights.
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Check file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    try:
        # Save to temp file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # Extract data from PDF
        extracted_data = extract_pdf_data(tmp_path)

        if not extracted_data["text"] and not extracted_data["tables"]:
            raise HTTPException(
                status_code=400,
                detail="Could not extract data from PDF. Please ensure it's a valid bank statement."
            )

        # Analyze with LLM
        analysis = await analyze_financial_data(extracted_data)

        return {
            "success": True,
            "data": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temp file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# Required for Vercel
handler = app
