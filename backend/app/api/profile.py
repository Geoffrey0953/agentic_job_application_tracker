from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import UserProfile
from app.schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse

router = APIRouter()

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(db: Session = Depends(get_db)):
    """
    Get the user profile (single profile for now, no auth)
    """
    profile = db.query(UserProfile).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@router.post("/profile", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update the user profile
    Since we're using a single profile (no auth), this will update if exists, create if not
    """
    try:
        # Check if profile exists
        existing_profile = db.query(UserProfile).first()
        
        if existing_profile:
            # Update existing profile
            update_dict = profile_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(existing_profile, key, value)
            db.commit()
            db.refresh(existing_profile)
            return existing_profile
        else:
            # Create new profile
            profile = UserProfile(**profile_data.dict())
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the user profile
    """
    profile = db.query(UserProfile).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        # Update fields that are provided
        update_dict = profile_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)
        
        db.commit()
        db.refresh(profile)
        
        return profile
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

