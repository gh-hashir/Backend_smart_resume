from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: str
    career_role: Optional[str] = None
    experience_level: Optional[str] = None
    location_preference: Optional[str] = None

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    full_name: Optional[str] = None
    career_role: Optional[str] = None
    experience_level: Optional[str] = None
    location_preference: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
