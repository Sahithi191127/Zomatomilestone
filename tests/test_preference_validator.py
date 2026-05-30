"""Tests for PreferenceValidator (Phase 2)."""

import pytest

from app.data.repository import RestaurantRepository
from app.exceptions import PreferenceValidationError
from app.models.restaurant import Restaurant
from app.services.preference_validator import (
    PreferenceValidator,
    suggest_locations,
    validate_preferences,
)


def _repo() -> RestaurantRepository:
    return RestaurantRepository(
        [
            Restaurant(
                id="1",
                name="Italian Spot",
                location="Banashankari",
                cuisines=["italian"],
                rating=4.5,
                estimated_cost=1200,
                budget_band="medium",
            ),
            Restaurant(
                id="2",
                name="BTM Cafe",
                location="Btm",
                cuisines=["chinese"],
                rating=4.0,
                estimated_cost=400,
                budget_band="low",
            ),
        ]
    )


class TestSuggestLocations:
    def test_prefix_match(self):
        cities = ["Banashankari", "Bellandur", "Btm"]
        assert suggest_locations("ban", cities)[0] == "Banashankari"

    def test_substring_match(self):
        cities = ["Banashankari", "Btm"]
        assert "Btm" in suggest_locations("bt", cities)


class TestPreferenceValidator:
    def test_valid_preferences(self):
        prefs = validate_preferences(
            {
                "location": "btm",
                "budget": "low",
                "cuisine": "chinese",
            },
            _repo(),
        )
        assert prefs.location == "Btm"
        assert prefs.budget == "low"

    def test_unknown_location_strict_raises(self):
        with pytest.raises(PreferenceValidationError) as exc_info:
            validate_preferences(
                {
                    "location": "Paris",
                    "budget": "low",
                    "cuisine": "French",
                },
                _repo(),
                strict_location=True,
            )
        err = exc_info.value
        assert err.field == "location"
        assert len(err.suggestions) >= 0

    def test_unknown_location_non_strict_passes(self):
        prefs = validate_preferences(
            {
                "location": "Paris",
                "budget": "low",
                "cuisine": "French",
            },
            _repo(),
            strict_location=False,
        )
        assert prefs.location == "Paris"

    def test_truncates_long_additional_preferences(self):
        repo = _repo()
        long_text = "a" * 600
        prefs = PreferenceValidator(repo, max_additional_length=500).validate(
            {
                "location": "Btm",
                "budget": "low",
                "cuisine": "chinese",
                "additional_preferences": long_text,
            }
        )
        assert prefs.additional_preferences is not None
        assert len(prefs.additional_preferences) == 500

    def test_pydantic_error_wrapped(self):
        with pytest.raises(PreferenceValidationError) as exc_info:
            validate_preferences(
                {"location": "Btm", "budget": "invalid", "cuisine": "x"},
                _repo(),
            )
        assert exc_info.value.field == "budget"

    def test_no_repo_skips_location_check(self):
        prefs = validate_preferences(
            {"location": "Unknown", "budget": "low", "cuisine": "x"},
            repository=None,
            strict_location=True,
        )
        assert prefs.location == "Unknown"
