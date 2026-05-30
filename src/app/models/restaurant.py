"""Canonical domain models (Data Architecture)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

BudgetBand = Literal["low", "medium", "high"]


class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: list[str]
    rating: float
    estimated_cost: float
    budget_band: BudgetBand
    metadata: dict[str, Any] = Field(default_factory=dict)


class FilterCriteria(BaseModel):
    """Structured filter dimensions (Component Design → 2, FilterCriteria)."""

    location: str | None = None
    budget: BudgetBand | None = None
    cuisine: str | None = None
    min_rating: float | None = None
