"""Join parsed LLM output with dataset Restaurant records."""

from __future__ import annotations

from app.models.recommendation import Recommendation, RecommendationMeta, RecommendationResponse
from app.models.restaurant import Restaurant
from app.services.response_parser import ParsedLLMResponse


def merge_llm_response(
    parsed: ParsedLLMResponse,
    candidates: list[Restaurant],
    *,
    candidates_considered: int,
    filters_applied: list[str],
    llm_model: str | None = None,
) -> RecommendationResponse:
    """Display fields always come from the repository / dataset."""
    by_id = {r.id: r for r in candidates}
    recommendations: list[Recommendation] = []

    for item in parsed.recommendations:
        restaurant = by_id.get(item.restaurant_id)
        if restaurant is None:
            continue
        recommendations.append(
            Recommendation(
                restaurant=restaurant,
                rank=item.rank,
                explanation=item.explanation,
            )
        )

    recommendations.sort(key=lambda r: r.rank)

    return RecommendationResponse(
        summary=parsed.summary,
        recommendations=recommendations,
        meta=RecommendationMeta(
            candidates_considered=candidates_considered,
            filters_applied=filters_applied,
            fallback_used=False,
            llm_model=llm_model,
        ),
    )
