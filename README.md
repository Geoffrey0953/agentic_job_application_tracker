# Agentic Job Application Tracker

An AI-powered job application tracker that automatically generates tailored resumes, cover letters, and ATS scores from a job description — using an agentic workflow built on AWS Bedrock (Claude).

---

## Features

- **Paste a job description** → AI analyzes it, generates a tailored resume, cover letter, and ATS match score
- **Agentic orchestration** — Claude dynamically plans and executes the workflow, with error recovery
- **Application dashboard** — track all applications with status, match scores, and generated documents
- **User profile** — store your work experience, education, skills, and projects once; AI uses it for every application
- **S3 document storage** — generated resumes and cover letters uploaded to AWS S3

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI | Claude via AWS Bedrock |
| Storage | AWS S3 |

---

## Project Structure

```
job_assistant_agent/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (applications, profile, agentic)
│   │   ├── db/            # Database session setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Bedrock AI service & agentic orchestrator
│   │   └── main.py        # FastAPI app entry point
│   └── requirements.txt
└── frontend/
    └── app/
        ├── page.tsx       # Dashboard
        └── profile/       # Profile management
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS account with Bedrock access (Claude model enabled in your region)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
DATABASE_URL=sqlite:///./jobtracker.db
S3_BUCKET_NAME=your_bucket_name   # optional
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`.

---

## How It Works

1. User pastes a job description into the dashboard
2. The **Agentic Orchestrator** calls Claude to plan a workflow
3. Claude executes each step:
   - Analyze job requirements
   - Fetch user profile from DB
   - Generate tailored resume
   - Generate cover letter
   - Calculate ATS match score
4. Results are saved to the database and optionally uploaded to S3
5. Application appears in the dashboard with all generated documents

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/applications` | List all applications |
| `DELETE` | `/api/applications/{id}` | Delete an application |
| `POST` | `/api/agentic/create-application` | Create application with AI workflow |
| `POST` | `/api/agentic/plan-workflow` | Preview the AI's planned steps |
| `GET` | `/api/profile` | Get user profile |
| `POST` | `/api/profile` | Create/update user profile |
