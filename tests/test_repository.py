"""Unit tests for RestaurantRepository (in-memory, no HF)."""

from app.data.repository import RestaurantRepository
from app.models.restaurant import FilterCriteria, Restaurant


def _make_repo() -> RestaurantRepository:
    restaurants = [
        Restaurant(
            id="1",
            name="Italian Spot",
            location="Bangalore",
            cuisines=["italian"],
            rating=4.5,
            estimated_cost=1200,
            budget_band="medium",
        ),
        Restaurant(
            id="2",
            name="Budget Chinese",
            location="Bangalore",
            cuisines=["chinese"],
            rating=4.0,
            estimated_cost=400,
            budget_band="low",
        ),
        Restaurant(
            id="3",
            name="Delhi Diner",
            location="Delhi",
            cuisines=["north indian"],
            rating=3.8,
            estimated_cost=800,
            budget_band="medium",
        ),
    ]
    return RestaurantRepository(restaurants)


class TestRestaurantRepository:
    def test_get_all(self):
        assert len(_make_repo().get_all()) == 3

    def test_get_by_ids(self):
        repo = _make_repo()
        found = repo.get_by_ids(["1", "missing", "2"])
        assert len(found) == 2
        assert found[0].id == "1"

    def test_get_cities_and_cuisines(self):
        repo = _make_repo()
        assert "Bangalore" in repo.get_cities()
        assert "italian" in repo.get_cuisines()

    def test_filter_location_budget_cuisine_rating(self):
        repo = _make_repo()
        criteria = FilterCriteria(
            location="Bangalore",
            budget="medium",
            cuisine="italian",
            min_rating=4.0,
        )
        results = repo.filter(criteria)
        assert len(results) == 1
        assert results[0].name == "Italian Spot"
