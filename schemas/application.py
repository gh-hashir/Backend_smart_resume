from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationBase(BaseModel):
    job_id: int
    status: Optional[str] = "Applied"
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
