"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import PROJECT_ROOT, get_cors_origins, settings
from app.dependencies import get_repository

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
    cors_kwargs: dict = {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.cors_allow_vercel_previews:
        cors_kwargs["allow_origin_regex"] = r"https://.*\.vercel\.app"
    app.add_middleware(CORSMiddleware, **cors_kwargs)

    @app.get("/", tags=["meta"])
    def api_root() -> dict[str, str]:
        return {
            "service": "TastePilot API",
            "health": "/api/v1/health",
            "docs": "/docs",
        }

    app.include_router(router)
    if IMAGES_DIR.is_dir():
        app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
    return app


app = create_app()
