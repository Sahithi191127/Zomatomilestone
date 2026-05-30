"""Recommendation output models (Data Architecture)."""

from pydantic import BaseModel, Field

from app.models.restaurant import Restaurant


class RecommendationMeta(BaseModel):
    """Response metadata (API Design)."""

    candidates_considered: int = 0
    filters_applied: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    llm_model: str | None = None


class Recommendation(BaseModel):
    restaurant: Restaurant
    rank: int = Field(ge=1)
    explanation: str


class RecommendationResponse(BaseModel):
    summary: str | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    meta: RecommendationMeta = Field(default_factory=RecommendationMeta)
