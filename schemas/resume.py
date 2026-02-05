from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

class ResumeBase(BaseModel):
    pass

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_path: Optional[str] = None
    parsed_data: Optional[Any] = None
    candidate_name: Optional[str] = "Applicant"
    recommended_fields: List[str] = []
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeAnalysisRequest(BaseModel):
    text: str

class DetailedBreakdownItem(BaseModel):
    category: str
    score: int
    comment: str

class AnalysisResponse(BaseModel):
    candidateName: Optional[str] = "Applicant"
    score: int
    matchRate: int
    strengths: List[str]
    gaps: List[str]
    detailedBreakdown: List[DetailedBreakdownItem]
    recommendedFields: List[str] = []
    feedback: str
