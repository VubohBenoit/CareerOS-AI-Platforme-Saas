"""Favorites API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/favorites", tags=["favorites"])

DEMO_FAVORITES = []

@router.get("/")
async def list_favorites(db: Session = Depends(get_db)):
    """List favorite jobs"""
    return DEMO_FAVORITES

@router.post("/{job_id}")
async def add_favorite(job_id: str, db: Session = Depends(get_db)):
    """Add job to favorites"""
    DEMO_FAVORITES.append({"job_id": job_id})
    return {"status": "added"}

@router.delete("/{job_id}")
async def remove_favorite(job_id: str, db: Session = Depends(get_db)):
    """Remove from favorites"""
    global DEMO_FAVORITES
    DEMO_FAVORITES = [f for f in DEMO_FAVORITES if f["job_id"] != job_id]
    return {"status": "removed"}
