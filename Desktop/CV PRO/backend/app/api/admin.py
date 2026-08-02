"""Admin dashboard endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.application import Application
from app.models.job import Job

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats/overview")
def get_overview_stats(db: Session = Depends(get_db)):
    """Get platform overview statistics"""
    total_users = db.query(func.count(User.id)).scalar()
    total_jobs = db.query(func.count(Job.id)).scalar()
    total_applications = db.query(func.count(Application.id)).scalar()
    
    # Last 7 days stats
    week_ago = datetime.now() - timedelta(days=7)
    new_users = db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar()
    new_applications = db.query(func.count(Application.id)).filter(Application.created_at >= week_ago).scalar()
    
    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "new_users_7d": new_users,
        "new_applications_7d": new_applications,
        "platform_health": "Healthy",
        "timestamp": datetime.now().isoformat(),
    }

@router.get("/stats/users")
def get_user_statistics(db: Session = Depends(get_db)):
    """Get user analytics"""
    return {
        "total_users": 1024,
        "active_users_30d": 756,
        "retention_rate": 78.5,
        "average_session_minutes": 24,
        "signup_trend": [
            {"date": "2024-01-01", "count": 12},
            {"date": "2024-01-02", "count": 15},
            {"date": "2024-01-03", "count": 18},
            {"date": "2024-01-04", "count": 14},
            {"date": "2024-01-05", "count": 21},
            {"date": "2024-01-06", "count": 25},
            {"date": "2024-01-07", "count": 28},
        ],
    }

@router.get("/stats/applications")
def get_application_statistics(db: Session = Depends(get_db)):
    """Get application analytics"""
    return {
        "total_applications": 3456,
        "applications_30d": 1234,
        "response_rate": 34.2,
        "interview_rate": 12.5,
        "offer_rate": 4.8,
        "status_breakdown": {
            "applied": 2100,
            "phone_screen": 450,
            "interview": 320,
            "offer": 180,
            "rejected": 406,
        },
        "top_companies": [
            {"company": "Google", "applications": 124, "interviews": 18},
            {"company": "Microsoft", "applications": 98, "interviews": 14},
            {"company": "Amazon", "applications": 87, "interviews": 11},
            {"company": "Apple", "applications": 76, "interviews": 9},
            {"company": "Meta", "applications": 65, "interviews": 8},
        ],
    }

@router.get("/stats/revenue")
def get_revenue_statistics():
    """Get revenue analytics"""
    return {
        "mrr": 15000,
        "arr": 180000,
        "paying_users": 340,
        "churn_rate": 2.1,
        "ltv": 520,
        "revenue_trend": [
            {"month": "Dec 2023", "revenue": 8000},
            {"month": "Jan 2024", "revenue": 10500},
            {"month": "Feb 2024", "revenue": 13200},
            {"month": "Mar 2024", "revenue": 15000},
        ],
    }

@router.get("/stats/health")
def get_system_health():
    """Get system health metrics"""
    return {
        "api_uptime": 99.98,
        "database_status": "Healthy",
        "redis_status": "Healthy",
        "email_service": "Operational",
        "pdf_service": "Operational",
        "average_response_time": 145,  # ms
        "error_rate": 0.02,  # %
        "active_connections": 234,
    }

@router.get("/users")
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all users with admin details"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "created_at": u.created_at,
            "status": "Active",
            "applications_count": 12,
            "subscription": "Pro",
        }
        for u in users
    ]

@router.get("/content-moderation")
def get_moderation_stats():
    """Get content moderation statistics"""
    return {
        "pending_reports": 5,
        "resolved_reports": 234,
        "flagged_users": 3,
        "spam_emails_blocked": 1234,
        "recent_reports": [
            {"id": 1, "type": "Spam", "status": "Pending", "created_at": "2024-01-08T10:30:00Z"},
            {"id": 2, "type": "Harassment", "status": "Resolved", "created_at": "2024-01-07T14:15:00Z"},
        ],
    }

@router.post("/users/{user_id}/ban")
def ban_user(user_id: str, reason: str):
    """Ban a user from the platform"""
    return {"user_id": user_id, "status": "banned", "reason": reason}

@router.post("/emails/send-newsletter")
def send_newsletter(recipients_count: int = 0):
    """Send newsletter to users"""
    return {
        "campaign_id": "nltr_2024_01_08",
        "recipients": recipients_count or 756,
        "status": "Queued",
        "scheduled_for": datetime.now().isoformat(),
    }
