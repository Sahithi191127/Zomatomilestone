"""End-to-end integration tests (Phase 5) with mocked LLM."""

import json

from app.data.repository import RestaurantRepository
from app.dependencies import reset_dependencies
from app.models.restaurant import Restaurant
from app.services.llm_client import CompletionOptions, LLMClient
from app.services.orchestrator import RecommendRestaurantsUseCase
from app.services.recommendation_engine import RecommendationEngine


class RecordingLLM(LLMClient):
    def __init__(self, response_json: dict) -> None:
        self.calls: list[list[dict[str, str]]] = []
        self._body = json.dumps(response_json)

    def complete(
        self,
        messages: list[dict[str, str]],
        options: CompletionOptions | None = None,
    ) -> str:
        self.calls.append(messages)
        return self._body


def test_dependencies_factory_with_in_memory_repo():
    reset_dependencies()
    repo = RestaurantRepository(
        [
            Restaurant(
                id="a1",
                name="Pizza Hub",
                location="Btm",
                cuisines=["italian"],
                rating=4.6,
                estimated_cost=900,
                budget_band="medium",
            ),
        ]
    )
    llm = RecordingLLM(
        {
            "summary": "One great pick.",
            "recommendations": [
                {"restaurant_id": "a1", "rank": 1, "explanation": "Perfect fit."},
            ],
        }
    )
    use_case = RecommendRestaurantsUseCase(
        repo,
        strict_location=False,
        recommendation_engine=RecommendationEngine(llm_client=llm),
    )

    response = use_case.execute(
        {
            "location": "Btm",
            "budget": "medium",
            "cuisine": "italian",
            "min_rating": 4.0,
            "top_k": 1,
        }
    )

    assert len(llm.calls) == 1
    assert response.recommendations[0].restaurant.name == "Pizza Hub"
    assert not response.meta.fallback_used
    assert response.summary == "One great pick."
