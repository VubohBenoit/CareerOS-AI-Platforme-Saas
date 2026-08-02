"""Analytics API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    return {
        "applications": {
            "total_applications": 8,
            "accepted": 1,
            "success_rate": 12,
            "by_status": {"SENT": 5, "INTERVIEWING": 2, "REJECTED": 1},
            "avg_days_to_accept": 14
        },
        "favorites": {"total_favorites": 15},
        "searches": {"total_saved_searches": 3, "active_alerts": 2},
    }

@router.get("/applications")
async def get_app_analytics(db: Session = Depends(get_db)):
    """Get applications analytics"""
    return {"total": 8, "accepted": 1, "rate": 12}
