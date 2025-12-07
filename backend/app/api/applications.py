from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter()

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job application
    """
    try:
        application = Application(
            job_title=application_data.job_title,
            company=application_data.company,
            location=application_data.location,
            job_description=application_data.job_description,
            job_url=application_data.job_url,
            status="pending"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return application
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications", response_model=List[ApplicationResponse])
async def get_applications(
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all applications, optionally filtered by status
    """
    query = db.query(Application)
    
    if status:
        query = query.filter(Application.status == status)
    
    applications = query.order_by(Application.created_at.desc()).all()
    return applications

@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific application by ID
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application

@router.put("/applications/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    update_data: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an application
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update fields that are provided
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(application, key, value)
    
    db.commit()
    db.refresh(application)
    
    return application

@router.delete("/applications/{application_id}")
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an application
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(application)
    db.commit()
    
    return {"success": True, "message": "Application deleted"}

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update just the status of an application
    """
    valid_statuses = ["pending", "applied", "interview", "offer", "rejected"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = status
    db.commit()
    
    return {"success": True, "status": status}