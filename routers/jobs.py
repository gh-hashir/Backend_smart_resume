from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import job as models
from schemas import job as schemas
from .auth import get_current_user
from models.user import User

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

@router.get("/", response_model=List[schemas.JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(models.Job).offset(skip).limit(limit).all()
    return jobs

@router.get("/match")
def get_matched_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Mock matching logic
    jobs = db.query(models.Job).limit(5).all()
    results = []
    for job in jobs:
        results.append({
            "job": job,
            "match_percentage": 95,
            "missing_skills": ["Kubernetes"]
        })
    return results

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
