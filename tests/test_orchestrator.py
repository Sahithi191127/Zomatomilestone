"""Tests for RecommendRestaurantsUseCase (Phase 5)."""

import json
import pytest

from app.data.repository import RestaurantRepository
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.llm_client import CompletionOptions, LLMClient
from app.services.orchestrator import RecommendRestaurantsUseCase


def _repo() -> RestaurantRepository:
    return RestaurantRepository(
        [
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
                name="Chinese Place",
                location="Btm",
                cuisines=["chinese"],
                rating=4.0,
                estimated_cost=500,
                budget_band="low",
            ),
        ]
    )


class MockLLM(LLMClient):
    def __init__(self) -> None:
        self.call_count = 0

    def complete(
        self,
        messages: list[dict[str, str]],
        options: CompletionOptions | None = None,
    ) -> str:
        self.call_count += 1
        return json.dumps(
            {
                "summary": "Great Italian options.",
                "recommendations": [
                    {
                        "restaurant_id": "r1",
                        "rank": 1,
                        "explanation": "Best Italian match.",
                    }
                ],
            }
        )


class TestRecommendRestaurantsUseCase:
    def test_execute_returns_all_display_fields(self):
        use_case = RecommendRestaurantsUseCase(_repo(), strict_location=False)
        mock = MockLLM()
        use_case._recommendation_engine._llm_client = mock  # noqa: SLF001

        response = use_case.execute(
            {
                "location": "Btm",
                "budget": "medium",
                "cuisine": "italian",
                "min_rating": 4.0,
                "top_k": 1,
            }
        )

        assert mock.call_count == 1
        assert len(response.recommendations) == 1
        rec = response.recommendations[0]
        assert rec.restaurant.name == "Italian Spot"
        assert rec.restaurant.rating == 4.5
        assert rec.restaurant.estimated_cost == 1200
        assert "italian" in rec.restaurant.cuisines
        assert rec.explanation == "Best Italian match."
        assert response.meta.candidates_considered >= 1
        assert "location" in response.meta.filters_applied

    def test_empty_filter_skips_llm_ec_orch_01(self):
        repo = RestaurantRepository(
            [
                Restaurant(
                    id="r1",
                    name="Only Chinese",
                    location="Btm",
                    cuisines=["chinese"],
                    rating=4.5,
                    estimated_cost=500,
                    budget_band="low",
                ),
            ]
        )
        mock = MockLLM()
        use_case = RecommendRestaurantsUseCase(repo, strict_location=False)
        use_case._recommendation_engine._llm_client = mock  # noqa: SLF001

        response = use_case.execute(
            UserPreferences(
                location="Btm",
                budget="medium",
                cuisine="italian",
                min_rating=4.0,
            )
        )

        assert mock.call_count == 0
        assert response.recommendations == []
        assert "No restaurants matched" in (response.summary or "")

    def test_display_fields_from_repository_not_llm(self):
        mock = MockLLM()
        use_case = RecommendRestaurantsUseCase(_repo(), strict_location=False)
        use_case._recommendation_engine._llm_client = mock  # noqa: SLF001

        response = use_case.execute(
            {
                "location": "Btm",
                "budget": "medium",
                "cuisine": "italian",
                "min_rating": 4.0,
                "top_k": 1,
            }
        )
        r = response.recommendations[0].restaurant
        assert r.name == "Italian Spot"
        assert r.id == "r1"
        assert r.budget_band == "medium"
