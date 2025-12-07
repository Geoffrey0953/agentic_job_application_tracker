from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, engine

class UserProfile(Base):
    """
    User profile with experiences, skills, education
    For now, we'll use a single profile (no auth)
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    summary = Column(Text)
    resume_text = Column(Text)  # Raw resume text that user pastes
    
    # Store as JSON arrays
    experiences = Column(JSON, default=list)  # [{"title": "...", "company": "...", "description": "...", "start_date": "...", "end_date": "..."}]
    education = Column(JSON, default=list)    # [{"degree": "...", "school": "...", "graduation_date": "..."}]
    skills = Column(JSON, default=list)       # ["Python", "AWS", "React", ...]
    projects = Column(JSON, default=list)     # [{"name": "...", "description": "...", "technologies": [...], "url": "..."}]
    certifications = Column(JSON, default=list)  # [{"name": "...", "issuer": "...", "date": "..."}]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Application(Base):
    """
    Job application tracking
    """
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic job info
    job_title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    job_description = Column(Text, nullable=False)
    job_url = Column(String(500))
    salary_range = Column(String(100))
    
    # Application status
    status = Column(String(50), default="pending")  # pending, applied, interview, offer, rejected
    applied_date = Column(DateTime, default=datetime.utcnow)
    
    # AI-generated analysis
    parsed_data = Column(JSON)  # Job analysis from Bedrock
    match_score = Column(Float)  # ATS match score (0-100)
    
    # Generated documents
    resume_content = Column(Text)
    resume_url = Column(String(500))
    cover_letter_content = Column(Text)
    cover_letter_url = Column(String(500))
    
    # Notes and tracking
    notes = Column(Text)
    interview_date = Column(DateTime)
    follow_up_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create all tables
def init_db():
    """
    Initialize database tables
    """
    Base.metadata.create_all(bind=engine)