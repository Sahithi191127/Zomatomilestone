"""Rating-based fallback when Groq is unavailable or parse fails."""

from __future__ import annotations

from app.models.recommendation import Recommendation, RecommendationMeta, RecommendationResponse
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.filter_service import sort_candidates

_MOOD_HINTS: dict[str, tuple[str, ...]] = {
    "date_night": ("romantic", "cozy", "rooftop", "fine", "quiet", "intimate", "lounge"),
    "family_dinner": ("family", "kids", "spacious", "casual", "buffet"),
    "quick_lunch": ("quick", "fast", "cafe", "snack", "express"),
    "friends_hangout": ("bar", "pub", "lounge", "lively", "group", "hangout"),
    "work_meeting": ("quiet", "business", "meeting", "cafe", "continental"),
    "solo_dining": ("cafe", "quiet", "cozy", "comfort"),
    "celebration_birthday": ("party", "celebration", "rooftop", "buffet", "lounge"),
    "casual_dining": ("casual", "comfort", "street", "quick"),
    "fine_dining": ("fine", "premium", "gourmet", "elegant", "continental"),
    "cafe_chill": ("cafe", "coffee", "dessert", "bakery", "relaxed"),
}


def _votes_key(restaurant: Restaurant) -> int:
    votes = restaurant.metadata.get("votes")
    if isinstance(votes, (int, float)):
        return int(votes)
    return 0


def _restaurant_text_blob(restaurant: Restaurant) -> str:
    bits = [restaurant.name, " ".join(restaurant.cuisines)]
    for value in restaurant.metadata.values():
        bits.append(str(value))
    return " ".join(bits).lower()


def _mood_score(restaurant: Restaurant, preferences: UserPreferences) -> int:
    if not preferences.mood:
        return 0

    score = 0
    blob = _restaurant_text_blob(restaurant)
    for token in _MOOD_HINTS.get(preferences.mood, ()):
        if token in blob:
            score += 2

    if preferences.mood == "fine_dining":
        if restaurant.budget_band == "high":
            score += 3
        if restaurant.rating >= 4.3:
            score += 2
    elif preferences.mood == "quick_lunch":
        if restaurant.budget_band in {"low", "medium"}:
            score += 2
        if restaurant.estimated_cost <= 600:
            score += 2
    elif preferences.mood == "work_meeting":
        if restaurant.rating >= 4.0:
            score += 1
    elif preferences.mood == "family_dinner":
        if restaurant.budget_band in {"low", "medium"}:
            score += 1

    return score


def _rank_for_fallback(
    candidates: list[Restaurant],
    preferences: UserPreferences,
) -> list[Restaurant]:
    # Base ordering remains rating/votes; mood score reorders ties and near-ties.
    pre_sorted = sort_candidates(candidates)
    return sorted(
        pre_sorted,
        key=lambda r: (-_mood_score(r, preferences), -r.rating, -_votes_key(r)),
    )


def _mood_phrase(mood: str | None) -> str:
    if not mood:
        return ""
    return mood.replace("_", " ")


def build_fallback_response(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    *,
    candidates_considered: int,
    filters_applied: list[str],
    llm_model: str | None = None,
) -> RecommendationResponse:
    """Top-K by pre-LLM sort with template explanations."""
    ranked = _rank_for_fallback(candidates, preferences)[: preferences.top_k]
    recommendations: list[Recommendation] = []

    for rank, restaurant in enumerate(ranked, start=1):
        cuisines = ", ".join(restaurant.cuisines[:3]) if restaurant.cuisines else preferences.cuisine
        explanation = (
            f"Rated {restaurant.rating:.1f}/5 for {cuisines} in {restaurant.location}, "
            f"within your {preferences.budget} budget (approx. Rs {restaurant.estimated_cost:.0f} for two)."
        )
        if preferences.mood:
            explanation += (
                f" This is ranked for a {_mood_phrase(preferences.mood)} occasion "
                f"using ambience and metadata keywords."
            )
        if preferences.additional_preferences:
            explanation += f" Note: {preferences.additional_preferences}."
        recommendations.append(
            Recommendation(
                restaurant=restaurant,
                rank=rank,
                explanation=explanation,
            )
        )

    summary = (
        f"Top {len(recommendations)} picks in {preferences.location} matching your "
        f"{preferences.cuisine} preference and {preferences.budget} budget "
        f"(AI ranking unavailable — sorted by rating)."
    )
    if preferences.mood:
        summary = (
            f"Top {len(recommendations)} picks for {_mood_phrase(preferences.mood)} in "
            f"{preferences.location}, matching your {preferences.cuisine} preference and "
            f"{preferences.budget} budget (AI ranking unavailable — mood-aware fallback used)."
        )

    return RecommendationResponse(
        summary=summary,
        recommendations=recommendations,
        meta=RecommendationMeta(
            candidates_considered=candidates_considered,
            filters_applied=filters_applied,
            fallback_used=True,
            llm_model=llm_model,
        ),
    )
