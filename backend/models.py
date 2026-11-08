from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    filename = Column(String(255), default="")
    job_title = Column(String(255), default="")
    job_description = Column(Text, default="")
    resume_text = Column(Text, default="")
    match_score = Column(Float, default=0)
    tfidf_score = Column(Float, default=0)
    skill_score = Column(Float, default=0)
    matched_skills = Column(Text, default="[]")  # JSON list
    missing_skills = Column(Text, default="[]")  # JSON list
    feedback = Column(Text, default="{}")  # JSON object from the LLM
    ai_source = Column(String(32), default="fallback")  # "gemini" or "fallback"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    title = Column(String(255), nullable=False)
    company = Column(String(255), default="")
    location = Column(String(255), default="")
    url = Column(String(1000), default="")
    description = Column(Text, nullable=False)
