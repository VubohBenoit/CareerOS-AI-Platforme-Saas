"""Main API Router - Combines all endpoint groups"""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.applications import router as applications_router
from app.api.recommendations import router as recommendations_router
from app.api.favorites import router as favorites_router
from app.api.saved_searches import router as saved_searches_router
from app.api.analytics import router as analytics_router

router = APIRouter(prefix="/api/v1")

# Include routers
router.include_router(auth_router)
router.include_router(jobs_router)
router.include_router(applications_router)
router.include_router(recommendations_router)
router.include_router(favorites_router)
router.include_router(saved_searches_router)
router.include_router(analytics_router)


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "CareerOS AI API v1",
        "status": "online",
        "version": "0.1.0",
    }
