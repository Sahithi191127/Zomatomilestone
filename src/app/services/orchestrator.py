"""
Recommendation Orchestrator — single entry point for the use case.

Architecture: Component Design → 7. Recommendation Orchestrator
Pipeline: validate → filter → (if empty return) → LLM engine → response
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.data.repository import RestaurantRepository
from app.models.recommendation import RecommendationResponse
from app.models.user_preferences import UserPreferences
from app.services.filter_service import FilterService
from app.services.preference_validator import PreferenceValidator
from app.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


class RecommendRestaurantsUseCase:
    """
    Coordinates validation, filtering, and LLM recommendation generation.

    This is the only service the API / UI layer should call for recommendations.
    """

    def __init__(
        self,
        repository: RestaurantRepository,
        *,
        filter_service: FilterService | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        validator: PreferenceValidator | None = None,
        strict_location: bool = True,
    ) -> None:
        self._repository = repository
        self._filter_service = filter_service or FilterService()
        self._recommendation_engine = recommendation_engine or RecommendationEngine()
        self._validator = validator or PreferenceValidator(
            repository,
            strict_location=strict_location,
        )

    def execute(
        self,
        preferences: dict[str, Any] | UserPreferences,
        *,
        request_id: str | None = None,
    ) -> RecommendationResponse:
        """
        Run the full recommendation pipeline.

        1. Validate preferences
        2. Filter candidates
        3. Generate recommendations (skips LLM when no candidates)
        """
        rid = request_id or str(uuid.uuid4())[:8]
        logger.info("request_id=%s starting recommendation pipeline", rid)

        prefs = self._validator.validate(preferences)
        filter_result = self._filter_service.filter(prefs, self._repository)

        logger.info(
            "request_id=%s filter complete candidates=%d total_before_cap=%d",
            rid,
            len(filter_result.candidates),
            filter_result.total_before_cap,
        )

        response = self._recommendation_engine.generate_from_candidates(
            prefs,
            filter_result,
        )

        logger.info(
            "request_id=%s complete recommendations=%d fallback=%s",
            rid,
            len(response.recommendations),
            response.meta.fallback_used,
        )
        return response
