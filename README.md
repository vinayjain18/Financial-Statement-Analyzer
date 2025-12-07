# FinSight

AI-powered financial statement analyzer that transforms bank statement PDFs into actionable insights.

## Features

- Upload bank statement PDFs and get instant analysis
- Automatic transaction categorization
- Income and expense breakdown with percentages
- Export reports as CSV or PDF
- Beautiful, responsive dashboard

## Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui

**Backend:**
- Python FastAPI
- pdfplumber (PDF extraction)
- OpenAI API (categorization only)

## How It Works

FinSight uses a hybrid approach for accurate financial analysis:

1. **Python Parsing** - Extracts transactions from PDF (dates, amounts, credit/debit type) with 100% accuracy
2. **LLM Categorization** - OpenAI categorizes transactions (food, bills, income, etc.)
3. **Python Calculations** - All totals computed using formula: `Closing Balance = Opening Balance + Credits - Debits`

This approach ensures accurate amounts while leveraging AI for intelligent categorization.

**Deployment:**
- Vercel (serverless)

## Security

FinSight implements multiple security measures to protect users:

- **Rate Limiting** - API requests are rate-limited to prevent abuse
- **CAPTCHA Protection** - hCaptcha integration to prevent automated attacks
- **File Validation** - Strict PDF validation (file type, content type, size limits)
- **CORS Protection** - Restricted to allowed origins only
- **No Data Storage** - Your documents are processed in memory and never stored

## Getting Started

### Frontend

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Backend

```bash
cd api

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env and add your API keys
cp .env.example .env

# Run server
uvicorn index:app --reload
```

API runs at [http://localhost:8000](http://localhost:8000)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/analyze` | POST | Analyze PDF statement |

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Optional (for production)
HCAPTCHA_SECRET_KEY=your-hcaptcha-secret
NEXT_PUBLIC_HCAPTCHA_SITE_KEY=your-hcaptcha-site-key
```
