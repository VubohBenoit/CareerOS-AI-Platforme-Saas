"""Main API Router - Combines all endpoint groups"""

from fastapi import APIRouter

# TODO: Import individual routers once they're implemented
# from app.api.auth import router as auth_router
# from app.api.profile import router as profile_router
# from app.api.jobs import router as jobs_router
# from app.api.applications import router as applications_router
# from app.api.documents import router as documents_router
# from app.api.interviews import router as interviews_router
# from app.api.analytics import router as analytics_router

router = APIRouter(prefix="/api/v1")

# Include routers
# router.include_router(auth_router, tags=["auth"])
# router.include_router(profile_router, tags=["profile"])
# router.include_router(jobs_router, tags=["jobs"])
# router.include_router(applications_router, tags=["applications"])
# router.include_router(documents_router, tags=["documents"])
# router.include_router(interviews_router, tags=["interviews"])
# router.include_router(analytics_router, tags=["analytics"])


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "CareerOS AI API v1",
        "status": "online",
    }
