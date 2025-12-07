from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.api import applications_router, profile_router, agent_router
from app.api import agentic as agentic_router
from app.models import init_db

load_dotenv()

app = FastAPI(
    title="Job Application Tracker API",
    description="AI-powered job application management with AWS Bedrock",
    version="1.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("⚠️  Please check your DATABASE_URL environment variable")
        print("⚠️  Example: DATABASE_URL=postgresql://user:password@localhost:5432/jobtracker")
        print("⚠️  Or use SQLite for development: DATABASE_URL=sqlite:///./jobtracker.db")

# Include API routers
app.include_router(applications_router, prefix="/api", tags=["Applications"])
app.include_router(profile_router, prefix="/api", tags=["Profile"])
app.include_router(agent_router, prefix="/api", tags=["AI Agent"])
app.include_router(agentic_router.router, prefix="/api", tags=["Agentic AI"])

@app.get("/")
def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "message": "Job Application Tracker API",
        "version": "1.0.0"
    }

@app.get("/api/status")
def api_status():
    """Detailed API status"""
    return {
        "api": "online",
        "aws_region": os.getenv("AWS_REGION", "not set"),
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured",
        "s3": "configured" if os.getenv("S3_BUCKET_NAME") else "not configured"
    }