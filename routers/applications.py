from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import application as models
from models import job as job_models
from schemas import application as schemas
from .auth import get_current_user
from models.user import User

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)

@router.get("/", response_model=List[schemas.ApplicationResponse])
def get_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Application).filter(models.Application.user_id == current_user.id).all()

@router.post("/", response_model=schemas.ApplicationResponse)
def create_application(
    application: schemas.ApplicationCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify job exists
    job = db.query(job_models.Job).filter(job_models.Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db_application = models.Application(
        user_id=current_user.id,
        job_id=application.job_id,
        status=application.status,
        notes=application.notes
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@router.put("/{application_id}", response_model=schemas.ApplicationResponse)
def update_application(
    application_id: int,
    application_update: schemas.ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_application = db.query(models.Application).filter(
        models.Application.id == application_id, 
        models.Application.user_id == current_user.id
    ).first()
    
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application_update.status:
        db_application.status = application_update.status
    if application_update.notes:
        db_application.notes = application_update.notes
        
    db.commit()
    db.refresh(db_application)
    return db_application
