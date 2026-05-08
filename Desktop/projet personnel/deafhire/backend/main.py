"""
DeafHire — FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from core.config import get_settings
from database import init_db
from routes.auth import router as auth_router
from routes.model import router as model_router
from routes.session import router as session_router
from routes.translation import router as translation_router
from routes.ws import router as ws_router

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s: %(message)s")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialise SQLite + seed default admin
    init_db()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de traduction LSF ↔ Texte pour entretiens inclusifs",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(model_router)
app.include_router(session_router)
app.include_router(translation_router)
app.include_router(ws_router)


# ── Health ────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


# ── Serve frontend in production ───────────────────────────
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
