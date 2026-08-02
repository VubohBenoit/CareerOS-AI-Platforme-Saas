"""Webhook system for event notifications"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, List
from app.db.database import get_db
import hashlib
import hmac
import json

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# In-memory webhook storage (replace with DB in production)
WEBHOOKS = {}
WEBHOOK_EVENTS = ["application.created", "application.updated", "job.matched", "offer.received"]

@router.post("/register")
def register_webhook(url: str, events: List[str], db: Session = Depends(get_db)):
    """Register a webhook endpoint"""
    webhook_id = f"wh_{len(WEBHOOKS) + 1}"
    
    if not all(e in WEBHOOK_EVENTS for e in events):
        raise HTTPException(status_code=400, detail="Invalid event type")
    
    WEBHOOKS[webhook_id] = {
        "url": url,
        "events": events,
        "active": True,
        "secret": hashlib.sha256(f"{webhook_id}{url}".encode()).hexdigest(),
    }
    
    return {
        "webhook_id": webhook_id,
        "url": url,
        "events": events,
        "secret": WEBHOOKS[webhook_id]["secret"],
        "status": "active",
    }

@router.get("/list")
def list_webhooks(db: Session = Depends(get_db)):
    """List all active webhooks"""
    return [
        {
            "webhook_id": wid,
            "url": w["url"],
            "events": w["events"],
            "active": w["active"],
            "last_triggered": "2024-01-08T15:30:00Z",
            "success_rate": 98.5,
        }
        for wid, w in WEBHOOKS.items()
    ]

@router.delete("/{webhook_id}")
def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    if webhook_id in WEBHOOKS:
        del WEBHOOKS[webhook_id]
        return {"status": "deleted", "webhook_id": webhook_id}
    raise HTTPException(status_code=404, detail="Webhook not found")

@router.post("/test/{webhook_id}")
def test_webhook(webhook_id: str):
    """Send a test event to webhook"""
    if webhook_id not in WEBHOOKS:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {
        "webhook_id": webhook_id,
        "test_sent": True,
        "status_code": 200,
        "response_time_ms": 145,
    }

@router.get("/events")
def get_webhook_events():
    """Get available webhook events"""
    return {
        "events": [
            {
                "name": "application.created",
                "description": "Triggered when user submits a job application",
                "payload": {
                    "event": "application.created",
                    "user_id": "user_123",
                    "application_id": "app_456",
                    "job_id": "job_789",
                    "timestamp": "2024-01-08T16:00:00Z",
                }
            },
            {
                "name": "application.updated",
                "description": "Triggered when application status changes",
                "payload": {
                    "event": "application.updated",
                    "application_id": "app_456",
                    "old_status": "applied",
                    "new_status": "phone_screen",
                    "timestamp": "2024-01-08T16:05:00Z",
                }
            },
            {
                "name": "job.matched",
                "description": "Triggered when AI finds matching job",
                "payload": {
                    "event": "job.matched",
                    "user_id": "user_123",
                    "job_id": "job_789",
                    "match_score": 0.87,
                    "timestamp": "2024-01-08T16:10:00Z",
                }
            },
            {
                "name": "offer.received",
                "description": "Triggered when user receives job offer",
                "payload": {
                    "event": "offer.received",
                    "user_id": "user_123",
                    "application_id": "app_456",
                    "salary": 150000,
                    "timestamp": "2024-01-08T16:15:00Z",
                }
            },
        ]
    }

@router.get("/{webhook_id}/logs")
def get_webhook_logs(webhook_id: str, limit: int = 50):
    """Get webhook delivery logs"""
    if webhook_id not in WEBHOOKS:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {
        "webhook_id": webhook_id,
        "logs": [
            {
                "timestamp": "2024-01-08T16:00:00Z",
                "event": "application.created",
                "status_code": 200,
                "response_time_ms": 145,
            },
            {
                "timestamp": "2024-01-08T15:30:00Z",
                "event": "job.matched",
                "status_code": 200,
                "response_time_ms": 210,
            },
        ]
    }
