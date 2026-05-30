"""Application dependencies — singleton repository and use-case factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.data.repository import RestaurantRepository
    from app.services.orchestrator import RecommendRestaurantsUseCase

_repository: RestaurantRepository | None = None


def get_repository(*, refresh: bool = False) -> "RestaurantRepository":
    """Load restaurant data once at startup (or refresh on demand)."""
    from app.data.repository import RestaurantRepository

    global _repository
    if _repository is None or refresh:
        _repository = RestaurantRepository.from_cache(refresh=refresh)
    return _repository


def get_recommendation_use_case(
    *,
    strict_location: bool = True,
    refresh_data: bool = False,
) -> "RecommendRestaurantsUseCase":
    """Factory for the main recommendation orchestrator."""
    from app.services.orchestrator import RecommendRestaurantsUseCase

    return RecommendRestaurantsUseCase(
        get_repository(refresh=refresh_data),
        strict_location=strict_location,
    )


def reset_dependencies() -> None:
    """Clear cached singletons (for tests)."""
    global _repository
    _repository = None
