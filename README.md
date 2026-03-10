# SANOVIO Procurement System

AI-powered procurement request management — create requests, extract vendor offer data with GPT-4o, and track status.

## Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB (local or Atlas)
- OpenAI API key

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENAI_API_KEY=sk-your-key
MONGODB_URI=mongodb://localhost:27017   # optional, this is the default
MONGODB_DB_NAME=procurement_db          # optional, this is the default
```

Run:

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at **http://localhost:8000** — API docs at **http://localhost:8000/docs**

### 2. Frontend

```bash
cd frontend/my-app
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, startup/shutdown
│   │   ├── routes/          # API endpoints (requests, ai, chat, metadata, conversations)
│   │   ├── services/        # Business logic (request, ai, chat, pdf)
│   │   ├── models/          # Pydantic schemas
│   │   ├── database.py      # MongoDB connection (async Motor)
│   │   ├── config.py        # Env config
│   │   └── constants.py     # Commodity groups & departments
│   ├── main.py              # Entry point
│   └── requirements.txt
│
├── frontend/my-app/
│   └── app/
│       ├── page.tsx          # Main SPA (4 tabs: Assistant, Intake, Overview, Settings)
│       ├── components/       # React components
│       ├── services/api.ts   # API client
│       ├── hooks/            # useToast, useFormValidation
│       └── types/            # TypeScript interfaces
│
├── diagrams/                 # Architecture diagrams (PNG images)
└── sample_vendor_offer.txt   # Test file for AI extraction
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 16, React 19, TypeScript 5, Tailwind CSS 4 |
| Backend | FastAPI 0.115, Pydantic 2.9, Motor 3.6 (async MongoDB) |
| Database | MongoDB |
| AI | OpenAI GPT-4o |

## Architecture Diagrams

See [`diagrams/`](./diagrams/) for full PNG architecture diagrams covering system overview, backend layers, frontend components, database schema, API endpoints, and user flow sequences.
