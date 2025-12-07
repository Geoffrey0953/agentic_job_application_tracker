from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Application, UserProfile
from app.schemas import AgentJobAnalysisRequest, AgentCreateApplicationRequest, AgentResponse
from app.services import bedrock_service, s3_service
from app.services.agentic_orchestrator import AgenticOrchestrator

router = APIRouter()

@router.post("/agent/analyze-job")
async def analyze_job_with_ai(request: AgentJobAnalysisRequest):
    """
    Analyze a job description using Claude
    """
    try:
        analysis = bedrock_service.analyze_job(request.job_description)
        
        return AgentResponse(
            success=True,
            message="Job analyzed successfully",
            data={"analysis": analysis}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/create-application")
async def create_application_with_ai(
    request: AgentCreateApplicationRequest,
    db: Session = Depends(get_db),
    use_agentic: bool = True  # New parameter to enable agentic mode
):
    """
    Create a complete job application with AI-generated resume and cover letter
    
    AGENTIC MODE (default): Uses AI to plan and execute workflow dynamically
    - Plans steps based on job description
    - Adapts to errors and recovers
    - Learns from past successful applications
    - Makes intelligent decisions about what to do
    
    LEGACY MODE: Fixed workflow (set use_agentic=False)
    """
    try:
        # Use agentic orchestrator if enabled
        if use_agentic:
            orchestrator = AgenticOrchestrator(db)
            result = orchestrator.create_application_agentic(
                request.job_description,
                request.auto_generate
            )
            
            if result["success"]:
                return AgentResponse(
                    success=True,
                    message="Application created with agentic AI workflow!",
                    data={
                        "application_id": result["application_id"],
                        "ats_score": result.get("ats_score"),
                        "execution_plan": result.get("plan"),
                        "execution_history": result.get("execution_result", {}).get("execution_history", []),
                        "agentic": True
                    }
                )
            else:
                # Fall back to legacy mode if agentic fails
                print("⚠️  Agentic mode failed, falling back to legacy mode")
                use_agentic = False
        
        # Legacy mode (original fixed workflow)
        if not use_agentic:
            # Step 1: Analyze job description
            job_analysis = bedrock_service.analyze_job(request.job_description)
            
            # Step 2: Create application in database
            application = Application(
                job_title=job_analysis.get('job_title', 'Unknown Position'),
                company=job_analysis.get('company', 'Unknown Company'),
                location=job_analysis.get('location', 'Unknown'),
                job_description=request.job_description,
                salary_range=job_analysis.get('salary_range'),
                parsed_data=job_analysis,
                status='pending'
            )
            
            db.add(application)
            db.commit()
            db.refresh(application)
            
            # Step 3: If auto_generate is True, generate documents
            if request.auto_generate:
                # Get user profile
                profile = db.query(UserProfile).first()
                
                if not profile:
                    return AgentResponse(
                        success=True,
                        message="Application created, but no profile found. Create a profile to generate resume and cover letter.",
                        data={
                            "application_id": application.id,
                            "analysis": job_analysis,
                            "needs_profile": True
                        }
                    )
                
                # Convert profile to dict
                profile_dict = {
                "full_name": profile.full_name,
                "email": profile.email,
                "phone": profile.phone,
                "linkedin_url": profile.linkedin_url,
                "github_url": profile.github_url,
                "portfolio_url": profile.portfolio_url,
                "summary": profile.summary,
                "resume_text": profile.resume_text,  # Include pasted resume text
                "experiences": profile.experiences or [],
                "education": profile.education or [],
                "skills": profile.skills or [],
                "projects": profile.projects or [],
                    "certifications": profile.certifications or []
                }
                
                # Step 4: Generate resume
                resume_content = bedrock_service.generate_resume(
                    job_analysis=job_analysis,
                    user_profile=profile_dict
                )
                
                # Step 5: Generate cover letter
                cover_letter_content = bedrock_service.generate_cover_letter(
                    job_analysis=job_analysis,
                    user_profile=profile_dict
                )
                
                # Step 6: Calculate ATS score
                ats_analysis = bedrock_service.calculate_ats_score(
                    resume_content=resume_content,
                    job_analysis=job_analysis
                )
                
                # Step 7: Upload to S3 (if configured)
                try:
                    resume_url = s3_service.upload_resume(resume_content, application.id)
                    cover_letter_url = s3_service.upload_cover_letter(cover_letter_content, application.id)
                except Exception as s3_error:
                    # If S3 fails, just store content in database
                    print(f"S3 upload failed: {s3_error}")
                    resume_url = None
                    cover_letter_url = None
                
                # Step 8: Update application with generated content
                application.resume_content = resume_content
                application.resume_url = resume_url
                application.cover_letter_content = cover_letter_content
                application.cover_letter_url = cover_letter_url
                application.match_score = ats_analysis.get('overall_score', 0)
                
                db.commit()
                db.refresh(application)
                
                return AgentResponse(
                    success=True,
                    message="Application created with AI-generated documents!",
                    data={
                        "application_id": application.id,
                        "analysis": job_analysis,
                        "ats_score": ats_analysis.get('overall_score'),
                        "ats_analysis": ats_analysis,
                        "resume_generated": True,
                        "cover_letter_generated": True,
                        "resume_url": resume_url,
                        "cover_letter_url": cover_letter_url,
                        "agentic": False
                    }
                )
            
            else:
                # Just return the application without generating documents
                return AgentResponse(
                    success=True,
                    message="Application created successfully",
                    data={
                        "application_id": application.id,
                        "analysis": job_analysis
                    }
                )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/generate-resume/{application_id}")
async def generate_resume_for_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate or regenerate resume for an existing application
    """
    try:
        # Get application
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get profile
        profile = db.query(UserProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile_dict = {
            "full_name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone,
            "linkedin_url": profile.linkedin_url,
            "github_url": profile.github_url,
            "summary": profile.summary,
            "resume_text": profile.resume_text,
            "experiences": profile.experiences or [],
            "education": profile.education or [],
            "skills": profile.skills or [],
            "projects": profile.projects or []
        }
        
        # Generate resume
        resume_content = bedrock_service.generate_resume(
            job_analysis=application.parsed_data or {},
            user_profile=profile_dict
        )
        
        # Upload to S3
        try:
            resume_url = s3_service.upload_resume(resume_content, application.id)
        except:
            resume_url = None
        
        # Update application
        application.resume_content = resume_content
        application.resume_url = resume_url
        db.commit()
        
        return AgentResponse(
            success=True,
            message="Resume generated successfully",
            data={
                "resume_content": resume_content,
                "resume_url": resume_url
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/generate-cover-letter/{application_id}")
async def generate_cover_letter_for_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate or regenerate cover letter for an existing application
    """
    try:
        # Get application
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get profile
        profile = db.query(UserProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile_dict = {
            "full_name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone,
            "summary": profile.summary,
            "experiences": profile.experiences or [],
            "skills": profile.skills or []
        }
        
        # Generate cover letter
        cover_letter_content = bedrock_service.generate_cover_letter(
            job_analysis=application.parsed_data or {},
            user_profile=profile_dict
        )
        
        # Upload to S3
        try:
            cover_letter_url = s3_service.upload_cover_letter(cover_letter_content, application.id)
        except:
            cover_letter_url = None
        
        # Update application
        application.cover_letter_content = cover_letter_content
        application.cover_letter_url = cover_letter_url
        db.commit()
        
        return AgentResponse(
            success=True,
            message="Cover letter generated successfully",
            data={
                "cover_letter_content": cover_letter_content,
                "cover_letter_url": cover_letter_url
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))