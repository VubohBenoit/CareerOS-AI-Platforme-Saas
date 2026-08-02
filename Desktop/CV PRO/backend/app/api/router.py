"""Main API Router - Combines all endpoint groups"""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.applications import router as applications_router
from app.api.recommendations import router as recommendations_router
from app.api.favorites import router as favorites_router
from app.api.saved_searches import router as saved_searches_router
from app.api.analytics import router as analytics_router
from app.api.admin import router as admin_router
from app.api.webhooks import router as webhooks_router
from app.api.jobs_integrated import router as jobs_integrated_router
from app.api.jobs_demo import router as jobs_demo_router
from app.api.documents import router as documents_router

router = APIRouter(prefix="/api/v1")

# Include routers
router.include_router(auth_router)
router.include_router(jobs_router)
router.include_router(jobs_demo_router)  # Demo jobs (no API keys needed)
router.include_router(jobs_integrated_router)  # Real job board integrations
router.include_router(applications_router)
router.include_router(recommendations_router)
router.include_router(favorites_router)
router.include_router(saved_searches_router)
router.include_router(analytics_router)
router.include_router(documents_router)  # Resume upload
router.include_router(admin_router)
router.include_router(webhooks_router)


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "CareerOS AI API v1",
        "status": "online",
        "version": "0.1.0",
    }
