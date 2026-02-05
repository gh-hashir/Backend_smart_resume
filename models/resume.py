from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, func
from sqlalchemy.orm import relationship
from database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    candidate_name = Column(String, nullable=True)
    recommended_fields = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="resumes")
