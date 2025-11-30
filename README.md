# FinSight

AI-powered financial statement analyzer that transforms bank statement PDFs into actionable insights.

## Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui

**Backend:**
- Python FastAPI
- pdfplumber (PDF extraction)
- OpenAI API (GPT-4o-mini)

**Deployment:**
- Vercel (serverless)

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

# Create .env file with your OpenAI key
echo OPENAI_API_KEY=sk-your-key > .env

# Run server
uvicorn index:app --reload
```

API runs at [http://localhost:8000](http://localhost:8000)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/python/health` | GET | Health check |
| `/api/python/analyze` | POST | Analyze PDF statement |

## Environment Variables

```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

