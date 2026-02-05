from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import re
import fitz  # PyMuPDF
import json
import google.generativeai as genai
from dotenv import load_dotenv
from database import get_db
from models import resume as models
from schemas import resume as schemas
from .auth import get_current_user
from models.user import User

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter(
    prefix="/resume",
    tags=["resume"],
)

@router.post("/analyze-match", response_model=schemas.AnalysisResponse)
async def analyze_resume_match(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # 1. Extract text from PDF
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported for now.")
        
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        resume_text = ""
        for page in doc:
            resume_text += page.get_text()
        doc.close()
        
        if not resume_text.strip():
            resume_text = f"Resume filename: {file.filename} (Empty or scanned PDF)"
            
    except Exception as e:
        print(f"Extraction error: {e}")
        resume_text = f"Could not extract text. Filename: {file.filename}"

    # 2. AI Analysis via Gemini
    try:
        # Reload env in case it changed
        load_dotenv()
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not key or "YOUR_GEMINI" in key:
            raise ValueError("GEMINI_API_KEY not found or still placeholder in environment.")

        # Re-configure to ensure the latest key is used
        genai.configure(api_key=key)
        
        print(f"DEBUG: Using Gemini API Key starting with: {key[:8]}...")

        # Use gemini-flash-latest as it's the most stable/supported alias with quota
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""
        You are an expert HR Specialist and ATS Optimizer. Your task is to analyze the provided document.
        
        1. If the document is a Resume:
           - Compare it against the provided Job Description.
           - Extract the Candidate's Full Name.
           - Calculate a Match Rate (0-100) and an Overall Suitability Score (0-100).
           - Identify 3 major strengths and 3 gaps.
           - Suggest 3 career fields or roles that best suit this candidate based on their background.
           - Provide a detailed breakdown in 3 categories (e.g., Skills, Experience, Formatting).
           - Provide a helpful overall feedback summary.

        2. If the document is NOT a Resume:
           - Extract a name if any name-like entity is present.
           - Return scores of 0.
           - In the 'feedback', explicitly state that the uploaded document does not appear to be a professional resume.
           - Still try to suggest what career fields might suit someone based on any text found.
        
        3. OUTPUT FORMAT:
           - You MUST return a STRICT JSON object with these EXACT keys:
             "candidateName" (string), "matchRate" (integer), "score" (integer), "strengths" (list of strings), 
             "gaps" (list of strings), "detailedBreakdown" (list of objects with "category", "score", "comment"), 
             "recommendedFields" (list of strings), "feedback" (string).

        Job Description:
        {job_description}

        Uploaded Document Text:
        {resume_text}
        """

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        analysis = json.loads(response.text)
        
        # Save to database if user is logged in
        if current_user:
            db_resume = models.Resume(
                user_id=current_user.id,
                file_path=f"http://localhost:8000/uploads/{file.filename}", # Mock path
                candidate_name=analysis.get("candidateName", "Applicant"),
                recommended_fields=analysis.get("recommendedFields", []),
                score=float(analysis.get("score", 0)),
                parsed_data={"analysis": analysis}
            )
            db.add(db_resume)
            db.commit()
            print(f"DEBUG: Saved resume for user {current_user.id}")

        return {
            "candidateName": analysis.get("candidateName", "Applicant"),
            "score": analysis.get("score", 0),
            "matchRate": analysis.get("matchRate", 0),
            "strengths": analysis.get("strengths", ["No strengths identified"]),
            "gaps": analysis.get("gaps", ["No specific gaps identified"]),
            "detailedBreakdown": analysis.get("detailedBreakdown", [
                {"category": "General", "score": 0, "comment": "Low match detected."}
            ]),
            "recommendedFields": analysis.get("recommendedFields", ["General Roles"]),
            "feedback": analysis.get("feedback", "Analysis complete.")
        }

    except Exception as e:
        print(f"AI Analysis error: {e}")
        # Dynamic fallback
        return {
            "candidateName": "Applicant",
            "score": 50,
            "matchRate": 45,
            "strengths": ["Document received"],
            "gaps": ["AI Analysis failed: " + str(e)],
            "detailedBreakdown": [
                {"category": "Status", "score": 50, "comment": "Analysis engine error."}
            ],
            "recommendedFields": ["Pending Analysis"],
            "feedback": "We encountered an error connecting to our AI engine. Please ensure your GEMINI_API_KEY is valid."
        }

@router.get("/", response_model=List[schemas.ResumeResponse])
def get_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Resume).filter(models.Resume.user_id == current_user.id).order_by(models.Resume.created_at.desc()).limit(5).all()

@router.get("/{resume_id}", response_model=schemas.ResumeResponse)
def get_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.post("/upload", response_model=schemas.ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fake_path = f"/uploads/{file.filename}"
    parsed_data = {"skills": ["Pending Analysis"], "education": "Pending Analysis"}
    
    db_resume = models.Resume(
        user_id=current_user.id,
        file_path=fake_path,
        parsed_data=parsed_data,
        score=0.0
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@router.put("/update", response_model=schemas.ResumeResponse)
def update_resume(
    resume_id: int,
    data: schemas.ResumeBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.commit()
    db.refresh(resume)
    return resume

@router.post("/improve-ai")
def improve_resume_ai(
    current_user: User = Depends(get_current_user)
):
    return {"message": "Resume improved by AI", "improved_text": "Enhanced bullet points..."}

@router.get("/score")
def get_resume_score(current_user: User = Depends(get_current_user)):
    return {"score": 0, "feedback": "Upload a resume for a detailed score"}
