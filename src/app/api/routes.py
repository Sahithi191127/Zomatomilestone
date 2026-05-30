"""REST routes for TastePilot React frontend."""

from __future__ import annotations

import logging
from time import perf_counter

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    HealthResponse,
    MetadataResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.config import settings
from app.dependencies import (
    get_recommendation_use_case,
    get_repository,
    repository_loaded_count,
)
from app.exceptions import PreferenceValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Fast liveness check for Railway (must respond before Parquet finishes loading).

    Returns 503 only when the catalog file is missing on disk.
    """
    if not settings.data_path.is_file():
        raise HTTPException(
            status_code=503,
            detail=f"Restaurant catalog file not found at {settings.data_path}",
        )
    count = repository_loaded_count()
    if count is None:
        return HealthResponse(status="ok", restaurants_loaded=0)
    return HealthResponse(status="ok", restaurants_loaded=count)


@router.get("/metadata/locations", response_model=MetadataResponse)
def list_locations() -> MetadataResponse:
    try:
        return MetadataResponse(items=get_repository().get_cities())
    except Exception as exc:
        logger.exception("metadata locations failed")
        raise HTTPException(status_code=503, detail="Restaurant catalog unavailable") from exc


@router.get("/metadata/cuisines", response_model=MetadataResponse)
def list_cuisines() -> MetadataResponse:
    try:
        return MetadataResponse(items=get_repository().get_cuisines())
    except Exception as exc:
        logger.exception("metadata cuisines failed")
        raise HTTPException(status_code=503, detail="Restaurant catalog unavailable") from exc


@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendations(body: RecommendationRequest) -> RecommendationResponse:
    use_case = get_recommendation_use_case(strict_location=True)
    started = perf_counter()
    try:
        response = use_case.execute(body.to_payload())
    except PreferenceValidationError as exc:
        detail = exc.to_dict()
        if exc.suggestions:
            detail["message"] = (
                f"{exc.message} Did you mean: {', '.join(exc.suggestions[:5])}?"
            )
        raise HTTPException(status_code=400, detail=detail) from exc
    except Exception as exc:
        logger.exception("recommendation pipeline failed")
        raise HTTPException(
            status_code=502,
            detail={"message": "Recommendation service failed. Please try again."},
        ) from exc

    elapsed_ms = int((perf_counter() - started) * 1000)
    logger.info(
        "recommendations complete count=%d elapsed_ms=%d",
        len(response.recommendations),
        elapsed_ms,
    )
    return response
