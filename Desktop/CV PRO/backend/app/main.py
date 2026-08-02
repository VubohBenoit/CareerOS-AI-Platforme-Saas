"""CareerOS AI - FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.router import router
from app.middleware.error_handling import error_handler_middleware
from app.middleware.logging import logging_middleware
from app.db.database import engine, Base

# Create tables on startup (in production, use Alembic migrations)
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle (startup/shutdown)."""
    # Startup
    print("🚀 CareerOS AI Backend starting...")
    yield
    # Shutdown
    print("🛑 CareerOS AI Backend shutting down...")


app = FastAPI(
    title="CareerOS AI",
    description="Intelligent AI-powered job search automation platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Middleware - CORS FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(logging_middleware)  # TODO: Fix middleware registration
# app.middleware("http")(error_handler_middleware)  # TODO: Fix middleware registration

# Routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Kubernetes liveness probe."""
    return {"status": "alive", "version": "0.1.0"}


@app.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe."""
    # TODO: Check database connection, Redis, etc.
    return {"status": "ready"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "CareerOS AI",
        "version": "0.1.0",
        "docs": "/api/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
