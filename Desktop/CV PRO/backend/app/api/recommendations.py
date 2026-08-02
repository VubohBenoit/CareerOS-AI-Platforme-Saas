"""Recommendations API endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
import uuid

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

DEMO_RECS = [
    {"id": str(uuid.uuid4()), "title": "Senior React Developer", "company": "TechCorp", "location": "Paris", "salary_min": 55000, "match_score": 95, "required_skills": ["React", "TypeScript"], "employment_type": "CDI", "description": "Perfect match"},
    {"id": str(uuid.uuid4()), "title": "Full Stack Engineer", "company": "StartupXYZ", "location": "Remote", "salary_min": 50000, "match_score": 87, "required_skills": ["JavaScript", "Python"], "employment_type": "CDI", "description": "Great opportunity"},
]

@router.get("/")
async def get_recommendations(sort: str = Query("score"), db: Session = Depends(get_db)):
    """Get AI recommendations"""
    return DEMO_RECS

@router.get("/stats")
async def get_recommendation_stats(db: Session = Depends(get_db)):
    """Get recommendation stats"""
    return {"total": len(DEMO_RECS), "avg_score": 91}
