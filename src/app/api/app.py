"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_cors_origins
from app.dependencies import get_repository

PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGES_DIR = PROJECT_ROOT / "images"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        get_repository()
    except Exception:
        pass
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="TastePilot API",
        description="Restaurant recommendations API for the TastePilot React UI",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    if IMAGES_DIR.is_dir():
        app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
    return app


app = create_app()
