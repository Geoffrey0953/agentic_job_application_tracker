from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============= User Profile Schemas =============

class ExperienceSchema(BaseModel):
    title: str
    company: str
    description: str
    start_date: str
    end_date: Optional[str] = "Present"

class EducationSchema(BaseModel):
    degree: str
    school: str
    graduation_date: str
    gpa: Optional[str] = None

class ProjectSchema(BaseModel):
    name: str
    description: str
    technologies: List[str]
    url: Optional[str] = None

class CertificationSchema(BaseModel):
    name: str
    issuer: str
    date: str

class UserProfileCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    resume_text: Optional[str] = None  # Raw resume text that user pastes
    experiences: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    skills: List[str] = []
    projects: List[ProjectSchema] = []
    certifications: List[CertificationSchema] = []

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    resume_text: Optional[str] = None
    experiences: Optional[List[ExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[ProjectSchema]] = None
    certifications: Optional[List[CertificationSchema]] = None

class UserProfileResponse(BaseModel):
    id: int
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    summary: Optional[str]
    resume_text: Optional[str]
    experiences: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    projects: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============= Application Schemas =============

class ApplicationCreate(BaseModel):
    job_title: str
    company: str
    location: Optional[str] = None
    job_description: str
    job_url: Optional[str] = None

class ApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None

class ApplicationResponse(BaseModel):
    id: int
    job_title: str
    company: str
    location: Optional[str]
    job_description: str
    job_url: Optional[str]
    salary_range: Optional[str]
    status: str
    applied_date: datetime
    parsed_data: Optional[Dict[str, Any]]
    match_score: Optional[float]
    resume_content: Optional[str]  # Generated resume content
    resume_url: Optional[str]
    cover_letter_content: Optional[str]  # Generated cover letter content
    cover_letter_url: Optional[str]
    notes: Optional[str]
    interview_date: Optional[datetime]
    follow_up_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============= Agent Schemas =============

class AgentJobAnalysisRequest(BaseModel):
    job_description: str

class AgentCreateApplicationRequest(BaseModel):
    job_description: str
    auto_generate: bool = True  # Automatically generate resume and cover letter

class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None