"""Saved Searches API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])

DEMO_SEARCHES = [
    {"id": "1", "name": "Remote React Jobs", "keywords": "React", "location": "Remote", "notify_enabled": True},
]

@router.get("/")
async def list_searches(db: Session = Depends(get_db)):
    """List saved searches"""
    return DEMO_SEARCHES

@router.post("/")
async def create_search(name: str, keywords: str = None, location: str = None, db: Session = Depends(get_db)):
    """Create saved search"""
    search = {"id": str(len(DEMO_SEARCHES)+1), "name": name, "keywords": keywords, "location": location, "notify_enabled": True}
    DEMO_SEARCHES.append(search)
    return search
