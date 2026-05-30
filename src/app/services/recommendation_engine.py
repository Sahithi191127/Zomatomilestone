"""
LLM recommendation engine (Phase 4).

Filter → prompt → Groq → parse → merge, with fallback on failure.
"""

from __future__ import annotations

import logging

from app.config import settings
from app.models.filter_result import FilterResult
from app.models.recommendation import RecommendationMeta, RecommendationResponse
from app.models.user_preferences import UserPreferences
from app.services.fallback_ranker import build_fallback_response
from app.services.llm_client import (
    LLMClient,
    LLMClientError,
    LLMRateLimitError,
    get_llm_client,
)
from app.services.prompt_builder import allowed_candidate_ids, build_messages
from app.services.recommendation_merger import merge_llm_response
from app.services.response_parser import ResponseParseError, parse_llm_response

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    def generate_from_candidates(
        self,
        preferences: UserPreferences,
        filter_result: FilterResult,
    ) -> RecommendationResponse:
        candidates = filter_result.candidates
        meta_base = {
            "candidates_considered": filter_result.total_before_cap,
            "filters_applied": filter_result.applied_filters,
        }

        if not candidates:
            return RecommendationResponse(
                summary=(
                    "No restaurants matched your filters. "
                    "Try a different location, cuisine, or lower minimum rating."
                ),
                recommendations=[],
                meta=RecommendationMeta(
                    candidates_considered=0,
                    filters_applied=filter_result.applied_filters,
                    fallback_used=False,
                ),
            )

        client = self._llm_client
        if client is None:
            if not settings.llm_api_key:
                logger.warning("LLM_API_KEY missing — using fallback ranker")
                return build_fallback_response(
                    preferences,
                    candidates,
                    candidates_considered=meta_base["candidates_considered"],
                    filters_applied=meta_base["filters_applied"],
                )
            try:
                client = get_llm_client()
            except LLMClientError as exc:
                logger.warning("LLM client unavailable: %s", exc)
                return build_fallback_response(
                    preferences,
                    candidates,
                    candidates_considered=meta_base["candidates_considered"],
                    filters_applied=meta_base["filters_applied"],
                )

        allowed_ids = allowed_candidate_ids(candidates)
        messages = build_messages(preferences, candidates)

        try:
            raw = client.complete(messages)
            parsed = parse_llm_response(
                raw,
                allowed_ids,
                top_k=preferences.top_k,
            )
            return merge_llm_response(
                parsed,
                candidates,
                candidates_considered=meta_base["candidates_considered"],
                filters_applied=meta_base["filters_applied"],
                llm_model=settings.llm_model,
            )
        except (LLMClientError, LLMRateLimitError, ResponseParseError) as exc:
            logger.warning("LLM pipeline failed (%s) — using fallback", exc)
            return build_fallback_response(
                preferences,
                candidates,
                candidates_considered=meta_base["candidates_considered"],
                filters_applied=meta_base["filters_applied"],
                llm_model=settings.llm_model,
            )
