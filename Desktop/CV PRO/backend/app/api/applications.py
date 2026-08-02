"""Applications API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from datetime import datetime
import uuid

router = APIRouter(prefix="/applications", tags=["applications"])

DEMO_APPLICATIONS = [
    {
        "id": str(uuid.uuid4()),
        "job_id": "1",
        "status": "SENT",
        "result": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "job_id": "2",
        "status": "INTERVIEWING",
        "result": None,
        "created_at": (datetime.utcnow()).isoformat(),
        "updated_at": (datetime.utcnow()).isoformat(),
    },
]

@router.get("/")
async def list_applications(db: Session = Depends(get_db)):
    """List all applications"""
    return DEMO_APPLICATIONS

@router.get("/{app_id}")
async def get_application(app_id: str, db: Session = Depends(get_db)):
    """Get a specific application"""
    app = next((a for a in DEMO_APPLICATIONS if a["id"] == app_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.post("/")
async def create_application(job_id: str, db: Session = Depends(get_db)):
    """Create a new application"""
    app = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "status": "DRAFT",
        "result": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    DEMO_APPLICATIONS.append(app)
    return app
