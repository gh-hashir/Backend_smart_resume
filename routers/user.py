from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import user as models
from schemas import user as schemas
from .auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/profile", response_model=schemas.UserResponse)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/profile", response_model=schemas.UserResponse)
def update_user_profile(
    profile_data: schemas.UserCreate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # In a real app we might want separate schemas for update vs create
    # For now, we just update fields if they are present
    current_user.career_role = profile_data.career_role
    current_user.experience_level = profile_data.experience_level
    current_user.location_preference = profile_data.location_preference
    
    db.commit()
    db.refresh(current_user)
    return current_user
