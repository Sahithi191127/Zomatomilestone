"""Tests for RecommendationEngine with mocked Groq."""

import json

import pytest

from app.models.filter_result import FilterResult
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.llm_client import CompletionOptions, LLMClient
from app.services.recommendation_engine import RecommendationEngine


def _candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Italian Spot",
            location="Btm",
            cuisines=["italian"],
            rating=4.5,
            estimated_cost=1200,
            budget_band="medium",
        ),
        Restaurant(
            id="r2",
            name="Chinese Garden",
            location="Btm",
            cuisines=["chinese"],
            rating=4.2,
            estimated_cost=600,
            budget_band="medium",
        ),
    ]


class MockLLMClient(LLMClient):
    def __init__(self, response: str) -> None:
        self._response = response
        self.calls = 0

    def complete(
        self,
        messages: list[dict[str, str]],
        options: CompletionOptions | None = None,
    ) -> str:
        self.calls = 1
        return self._response


class TestRecommendationEngine:
    def test_empty_candidates_skips_llm(self):
        prefs = UserPreferences(location="Btm", budget="medium", cuisine="italian")
        mock = MockLLMClient("{}")
        engine = RecommendationEngine(llm_client=mock)
        result = engine.generate_from_candidates(
            prefs,
            FilterResult(candidates=[], total_before_cap=0, applied_filters=[]),
        )
        assert result.recommendations == []
        assert mock.calls == 0

    def test_groq_success_merges_dataset_fields(self):
        raw = json.dumps(
            {
                "summary": "Best Italian in Btm.",
                "recommendations": [
                    {
                        "restaurant_id": "r1",
                        "rank": 1,
                        "explanation": "Perfect Italian match.",
                    }
                ],
            }
        )
        mock = MockLLMClient(raw)
        prefs = UserPreferences(
            location="Btm",
            budget="medium",
            cuisine="italian",
            top_k=1,
        )
        engine = RecommendationEngine(llm_client=mock)
        result = engine.generate_from_candidates(
            prefs,
            FilterResult(
                candidates=_candidates(),
                total_before_cap=2,
                applied_filters=["location", "budget", "cuisine", "min_rating"],
            ),
        )
        assert mock.calls == 1
        assert not result.meta.fallback_used
        assert result.summary == "Best Italian in Btm."
        assert len(result.recommendations) == 1
        assert result.recommendations[0].restaurant.name == "Italian Spot"
        assert result.recommendations[0].explanation == "Perfect Italian match."

    def test_parse_failure_uses_fallback(self):
        mock = MockLLMClient("not valid json")
        prefs = UserPreferences(location="Btm", budget="medium", cuisine="italian", top_k=2)
        engine = RecommendationEngine(llm_client=mock)
        result = engine.generate_from_candidates(
            prefs,
            FilterResult(
                candidates=_candidates(),
                total_before_cap=2,
                applied_filters=["location"],
            ),
        )
        assert result.meta.fallback_used
        assert len(result.recommendations) == 2
        assert result.recommendations[0].restaurant.id == "r1"

    def test_no_hallucinated_ids_in_output(self):
        raw = json.dumps(
            {
                "summary": "Ok",
                "recommendations": [
                    {"restaurant_id": "r1", "rank": 1, "explanation": "Good"},
                    {"restaurant_id": "fake99", "rank": 2, "explanation": "Bad"},
                ],
            }
        )
        engine = RecommendationEngine(llm_client=MockLLMClient(raw))
        prefs = UserPreferences(location="Btm", budget="medium", cuisine="italian", top_k=5)
        result = engine.generate_from_candidates(
            prefs,
            FilterResult(candidates=_candidates(), total_before_cap=2, applied_filters=[]),
        )
        ids = {r.restaurant.id for r in result.recommendations}
        assert "fake99" not in ids
        assert ids <= {"r1", "r2"}

    def test_fallback_ranking_uses_mood_keywords(self):
        candidates = [
            Restaurant(
                id="r1",
                name="Premium Bistro",
                location="Btm",
                cuisines=["italian"],
                rating=4.6,
                estimated_cost=1800,
                budget_band="high",
                metadata={"rest_type": "fine dining"},
            ),
            Restaurant(
                id="r2",
                name="Quick Bite Express",
                location="Btm",
                cuisines=["fast food"],
                rating=4.2,
                estimated_cost=350,
                budget_band="low",
                metadata={"rest_type": "quick bites"},
            ),
        ]
        mock = MockLLMClient("not valid json")
        prefs = UserPreferences(
            location="Btm",
            budget="medium",
            cuisine="italian",
            top_k=1,
            mood="quick_lunch",
        )
        engine = RecommendationEngine(llm_client=mock)
        result = engine.generate_from_candidates(
            prefs,
            FilterResult(
                candidates=candidates,
                total_before_cap=2,
                applied_filters=["location"],
            ),
        )
        assert result.meta.fallback_used
        assert result.recommendations[0].restaurant.id == "r2"
