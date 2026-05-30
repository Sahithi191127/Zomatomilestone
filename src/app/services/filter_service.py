"""
FilterService — deterministic filtering and pre-LLM candidate preparation.

Architecture: filter before generate; cap at MAX_CANDIDATES; additional_preferences
are NOT applied structurally (forwarded to LLM in Phase 4+).
"""

from __future__ import annotations

from typing import Literal

from app.config import settings
from app.data.repository import RestaurantRepository
from app.models.filter_result import FilterResult
from app.models.restaurant import FilterCriteria, Restaurant
from app.models.user_preferences import UserPreferences

LocationMatchMode = Literal["substring", "exact"]


def _votes_key(restaurant: Restaurant) -> int:
    votes = restaurant.metadata.get("votes")
    if isinstance(votes, (int, float)):
        return int(votes)
    return 0


def sort_candidates(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Post-filter ranking: rating desc, then votes in metadata if present."""
    return sorted(
        restaurants,
        key=lambda r: (-r.rating, -_votes_key(r)),
    )


class FilterService:
    def __init__(
        self,
        max_candidates: int | None = None,
        location_match: LocationMatchMode | None = None,
    ) -> None:
        self._max_candidates = max_candidates or settings.max_candidates
        self._location_match: LocationMatchMode = (
            location_match or settings.location_match_mode
        )

    def filter(
        self,
        preferences: UserPreferences,
        repository: RestaurantRepository,
    ) -> FilterResult:
        criteria = preferences.to_filter_criteria()
        applied_filters = _applied_filter_names(criteria)

        matches = repository.filter(criteria)
        matches = _apply_location_mode(matches, criteria.location, self._location_match)

        total_before_cap = len(matches)
        ranked = sort_candidates(matches)
        candidates = ranked[: self._max_candidates]

        return FilterResult(
            candidates=candidates,
            total_before_cap=total_before_cap,
            applied_filters=applied_filters,
        )


def _applied_filter_names(criteria: FilterCriteria) -> list[str]:
    names: list[str] = []
    if criteria.location:
        names.append("location")
    if criteria.budget:
        names.append("budget")
    if criteria.cuisine:
        names.append("cuisine")
    if criteria.min_rating is not None:
        names.append("min_rating")
    return names


def _apply_location_mode(
    restaurants: list[Restaurant],
    location: str | None,
    mode: LocationMatchMode,
) -> list[Restaurant]:
    if not location or mode == "substring":
        return restaurants
    loc = location.strip().lower()
    return [r for r in restaurants if r.location.lower() == loc]
