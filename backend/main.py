import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

load_dotenv()

import models  # noqa: E402
from database import Base, SessionLocal, engine, get_db  # noqa: E402
from llm import generate_feedback  # noqa: E402
from nlp import compute_match  # noqa: E402
from pdf_utils import PDFError, extract_text  # noqa: E402
from seed import SEED_JOBS  # noqa: E402

MAX_PDF_BYTES = 5 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Job).count() == 0:
            db.add_all([models.Job(**j) for j in SEED_JOBS])
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="AI Resume Analyzer", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def loads(value, default):
    try:
        return json.loads(value) if value else default
    except json.JSONDecodeError:
        return default


def analysis_out(a: models.Analysis, full: bool = True) -> dict:
    data = {
        "id": a.id,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "filename": a.filename,
        "job_title": a.job_title,
        "match_score": a.match_score,
        "matched_count": len(loads(a.matched_skills, [])),
        "missing_count": len(loads(a.missing_skills, [])),
        "ai_source": a.ai_source,
    }
    if full:
        data.update({
            "job_description": a.job_description,
            "tfidf_score": a.tfidf_score,
            "skill_score": a.skill_score,
            "matched_skills": loads(a.matched_skills, []),
            "missing_skills": loads(a.missing_skills, []),
            "feedback": loads(a.feedback, {}),
        })
    return data


def job_out(j: models.Job) -> dict:
    return {
        "id": j.id, "title": j.title, "company": j.company,
        "location": j.location, "url": j.url, "description": j.description,
    }


@app.get("/")
def root():
    return {"name": "AI Resume Analyzer API", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_enabled": bool(os.getenv("GEMINI_API_KEY", "").strip())}


# ---------- Analyses ----------
@app.post("/api/analyze")
def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: str = Form(""),
    db: Session = Depends(get_db),
):
    job_description = job_description.strip()
    if len(job_description) < 30:
        raise HTTPException(422, "Please paste a longer job description (at least 30 characters).")

    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(422, "Please upload a PDF file.")
    data = file.file.read(MAX_PDF_BYTES + 1)
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF is too large. Maximum size is 5 MB.")
    try:
        resume_text = extract_text(data)
    except PDFError as exc:
        raise HTTPException(422, str(exc))

    match = compute_match(resume_text, job_description)
    feedback, source = generate_feedback(
        resume_text, job_description, job_title.strip(),
        match["match_score"], match["matched_skills"], match["missing_skills"],
    )

    analysis = models.Analysis(
        filename=file.filename[:255],
        job_title=job_title.strip()[:255],
        job_description=job_description,
        resume_text=resume_text,
        match_score=match["match_score"],
        tfidf_score=match["tfidf_score"],
        skill_score=match["skill_score"],
        matched_skills=json.dumps(match["matched_skills"]),
        missing_skills=json.dumps(match["missing_skills"]),
        feedback=json.dumps(feedback),
        ai_source=source,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis_out(analysis)


@app.get("/api/analyses")
def list_analyses(db: Session = Depends(get_db)):
    rows = db.query(models.Analysis).order_by(models.Analysis.id.desc()).limit(100).all()
    return [analysis_out(a, full=False) for a in rows]


@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    a = db.get(models.Analysis, analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found.")
    return analysis_out(a)


@app.delete("/api/analyses/{analysis_id}")
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    a = db.get(models.Analysis, analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found.")
    db.delete(a)
    db.commit()
    return {"ok": True}


# ---------- Jobs ----------
class JobIn(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    company: str = Field(default="", max_length=255)
    location: str = Field(default="", max_length=255)
    url: str = Field(default="", max_length=1000)
    description: str = Field(min_length=30)


@app.get("/api/jobs")
def list_jobs(db: Session = Depends(get_db)):
    return [job_out(j) for j in db.query(models.Job).order_by(models.Job.id.desc()).all()]


@app.post("/api/jobs")
def create_job(payload: JobIn, db: Session = Depends(get_db)):
    job = models.Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_out(job)


@app.post("/api/jobs/bulk")
def bulk_create_jobs(payload: list[JobIn], db: Session = Depends(get_db)):
    """Import many jobs at once, e.g. exported from your Job Hunt project."""
    if len(payload) > 500:
        raise HTTPException(413, "Send at most 500 jobs at a time.")
    jobs = [models.Job(**p.model_dump()) for p in payload]
    db.add_all(jobs)
    db.commit()
    return {"created": len(jobs)}


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    db.delete(job)
    db.commit()
    return {"ok": True}


@app.get("/api/analyses/{analysis_id}/rank-jobs")
def rank_jobs(analysis_id: int, db: Session = Depends(get_db)):
    a = db.get(models.Analysis, analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found.")
    results = []
    for job in db.query(models.Job).all():
        text = f"{job.title}. {job.description}"
        m = compute_match(a.resume_text, text)
        results.append({
            **job_out(job),
            "match_score": m["match_score"],
            "matched_skills": m["matched_skills"],
            "missing_skills": m["missing_skills"],
        })
    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results
