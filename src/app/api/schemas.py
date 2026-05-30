"""API request/response schemas (ARCHITECTURE.md § API Design)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.recommendation import RecommendationResponse
from app.models.restaurant import BudgetBand

BudgetBandApi = Literal["low", "medium", "high"]


class RecommendationRequest(BaseModel):
    location: str
    budget: BudgetBand
    cuisine: str
    min_rating: float = Field(default=2.9, ge=0.0, le=5.0)
    additional_preferences: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    mood: str | None = None

    def to_payload(self) -> dict:
        return self.model_dump(exclude_none=True)


class HealthResponse(BaseModel):
    status: str = "ok"
    restaurants_loaded: int = 0


class MetadataResponse(BaseModel):
    items: list[str]


class ErrorDetail(BaseModel):
    message: str
    field: str | None = None
    suggestions: list[str] = Field(default_factory=list)


# Re-export response model for OpenAPI
__all__ = [
    "RecommendationRequest",
    "RecommendationResponse",
    "HealthResponse",
    "MetadataResponse",
    "ErrorDetail",
]
