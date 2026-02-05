from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)

class Settings(BaseModel):
    auto_apply: bool
    daily_limit: int
    resume_id: int

@router.get("/", response_model=Settings)
def get_settings():
    return Settings(auto_apply=True, daily_limit=50, resume_id=1)

@router.put("/")
def update_settings(settings: Settings):
    return settings
