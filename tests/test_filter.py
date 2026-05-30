"""Tests for FilterService (Phase 3, EC-FIL-*)."""

import pytest

from app.data.repository import RestaurantRepository
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.context_serializer import build_llm_context, serialize_candidates
from app.services.filter_service import FilterService, sort_candidates


def _repo() -> RestaurantRepository:
    """Fixture aligned with acceptance: Bangalore + medium + Italian + 4.0."""
    restaurants = [
        Restaurant(
            id="1",
            name="Italian Spot",
            location="Bangalore",
            cuisines=["italian", "continental"],
            rating=4.5,
            estimated_cost=1200,
            budget_band="medium",
            metadata={"votes": 500},
        ),
        Restaurant(
            id="2",
            name="Medium Chinese",
            location="Bangalore",
            cuisines=["chinese"],
            rating=4.2,
            estimated_cost=900,
            budget_band="medium",
            metadata={"votes": 800},
        ),
        Restaurant(
            id="3",
            name="Low Italian",
            location="Bangalore",
            cuisines=["italian"],
            rating=3.9,
            estimated_cost=400,
            budget_band="low",
            metadata={"votes": 100},
        ),
        Restaurant(
            id="4",
            name="High Rated Delhi Italian",
            location="Delhi",
            cuisines=["italian"],
            rating=4.8,
            estimated_cost=1500,
            budget_band="high",
            metadata={"votes": 200},
        ),
        Restaurant(
            id="5",
            name="Bangalore Medium Diner",
            location="Bangalore",
            cuisines=["north indian"],
            rating=4.1,
            estimated_cost=700,
            budget_band="medium",
            metadata={"votes": 50},
        ),
    ]
    return RestaurantRepository(restaurants)


def _prefs(**kwargs) -> UserPreferences:
    defaults = {
        "location": "Bangalore",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
    }
    defaults.update(kwargs)
    return UserPreferences(**defaults)


class TestFilterService:
    def test_bangalore_medium_italian_min_rating(self):
        result = FilterService(max_candidates=30).filter(_prefs(), _repo())
        assert result.total_before_cap == 1
        assert len(result.candidates) == 1
        assert result.candidates[0].name == "Italian Spot"
        assert result.candidates[0].id == "1"

    def test_applied_filters_list(self):
        result = FilterService().filter(_prefs(), _repo())
        assert result.applied_filters == ["location", "budget", "cuisine", "min_rating"]

    def test_zero_matches_ec_fil_01(self):
        result = FilterService().filter(
            _prefs(location="Mumbai", cuisine="Mexican"),
            _repo(),
        )
        assert result.is_empty
        assert result.total_before_cap == 0
        assert result.candidates == []

    def test_cap_ec_fil_02(self):
        many = [
            Restaurant(
                id=str(i),
                name=f"R{i}",
                location="Bangalore",
                cuisines=["italian"],
                rating=4.0 + i * 0.01,
                estimated_cost=1000,
                budget_band="medium",
                metadata={"votes": i},
            )
            for i in range(50)
        ]
        repo = RestaurantRepository(many)
        result = FilterService(max_candidates=10).filter(_prefs(), repo)
        assert result.total_before_cap == 50
        assert len(result.candidates) == 10

    def test_sort_by_rating_then_votes(self):
        ranked = sort_candidates(_repo().filter(_prefs().to_filter_criteria()))
        assert ranked[0].name == "Italian Spot"
        assert ranked[0].rating >= ranked[-1].rating

    def test_additional_preferences_not_filtered_ec_fil_03(self):
        """Same structural result with or without additional_preferences."""
        base = FilterService().filter(_prefs(), _repo())
        with_extra = FilterService().filter(
            _prefs(additional_preferences="family-friendly, quiet"),
            _repo(),
        )
        assert [c.id for c in base.candidates] == [c.id for c in with_extra.candidates]

    def test_case_insensitive_location_and_cuisine_ec_fil_04(self):
        result = FilterService().filter(
            _prefs(location="bangalore", cuisine="ITALIAN"),
            _repo(),
        )
        assert len(result.candidates) == 1

    def test_exact_location_mode(self):
        repo = RestaurantRepository(
            [
                Restaurant(
                    id="a",
                    name="A",
                    location="BTM Layout",
                    cuisines=["italian"],
                    rating=4.5,
                    estimated_cost=800,
                    budget_band="medium",
                ),
                Restaurant(
                    id="b",
                    name="B",
                    location="BTM",
                    cuisines=["italian"],
                    rating=4.4,
                    estimated_cost=800,
                    budget_band="medium",
                ),
            ]
        )
        prefs = UserPreferences(location="BTM", budget="medium", cuisine="italian")
        substring = FilterService(location_match="substring").filter(prefs, repo)
        exact = FilterService(location_match="exact").filter(prefs, repo)
        assert len(substring.candidates) == 2
        assert len(exact.candidates) == 1
        assert exact.candidates[0].location == "BTM"

    def test_all_candidate_ids_in_repository(self):
        repo = _repo()
        known = {r.id for r in repo.get_all()}
        result = FilterService().filter(_prefs(), repo)
        assert all(c.id in known for c in result.candidates)

    def test_min_rating_inclusive_ec_fil_06(self):
        """rating >= min_rating: 4.1 included at 4.1, excluded at 4.2."""
        assert len(FilterService().filter(_prefs(min_rating=4.1), _repo()).candidates) == 1
        assert FilterService().filter(_prefs(min_rating=4.2), _repo()).candidates[0].name == "Italian Spot"
        assert (
            len(
                FilterService()
                .filter(_prefs(min_rating=4.6), _repo())
                .candidates
            )
            == 0
        )


class TestContextSerializer:
    def test_serialize_minimal_fields(self):
        repo = _repo()
        candidates = FilterService().filter(_prefs(), repo).candidates
        payload = serialize_candidates(candidates)
        assert set(payload[0].keys()) == {
            "id",
            "name",
            "location",
            "cuisines",
            "rating",
            "estimated_cost",
            "budget_band",
        }

    def test_build_llm_context_includes_preferences(self):
        prefs = _prefs(additional_preferences="quiet")
        ctx = build_llm_context(prefs, [])
        assert ctx["preferences"]["additional_preferences"] == "quiet"
        assert ctx["candidates"] == []
