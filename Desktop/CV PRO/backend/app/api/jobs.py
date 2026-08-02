"""Jobs API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.job import JobPosting
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Demo jobs data
DEMO_JOBS = [
    {
        "id": str(uuid.uuid4()),
        "title": "Senior React Developer",
        "company": "TechCorp",
        "location": "Paris, France",
        "salary_min": 55000,
        "salary_max": 75000,
        "description": "Join our team to build amazing web applications with React and TypeScript",
        "required_skills": ["React", "TypeScript", "Node.js", "PostgreSQL"],
        "employment_type": "CDI",
        "posted_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Full Stack Engineer",
        "company": "StartupXYZ",
        "location": "Remote",
        "salary_min": 50000,
        "salary_max": 70000,
        "description": "Build scalable backend and frontend solutions for our platform",
        "required_skills": ["JavaScript", "Python", "AWS", "Docker"],
        "employment_type": "CDI",
        "posted_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "title": "DevOps Engineer",
        "company": "CloudInc",
        "location": "Lyon, France",
        "salary_min": 45000,
        "salary_max": 65000,
        "description": "Manage our cloud infrastructure and CI/CD pipelines",
        "required_skills": ["Kubernetes", "Docker", "AWS", "Terraform"],
        "employment_type": "CDI",
        "posted_date": datetime.utcnow().isoformat(),
    },
]

@router.get("/")
async def list_jobs(
    search: str = Query(None),
    location: str = Query(None),
    salary_min: int = Query(None),
    db: Session = Depends(get_db),
):
    """List all jobs with optional filters"""
    jobs = DEMO_JOBS

    if search:
        jobs = [j for j in jobs if search.lower() in j["title"].lower() or search.lower() in j["company"].lower()]
    if location:
        jobs = [j for j in jobs if location.lower() in j["location"].lower()]
    if salary_min:
        jobs = [j for j in jobs if j.get("salary_min", 0) >= salary_min]

    return jobs

@router.get("/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = next((j for j in DEMO_JOBS if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/trending/jobs")
async def get_trending_jobs(db: Session = Depends(get_db)):
    """Get trending jobs"""
    return DEMO_JOBS[:2]
