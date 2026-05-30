"""Unit tests for domain models (Phase 2)."""

import json

import pytest
from pydantic import ValidationError

from app.models.recommendation import Recommendation, RecommendationResponse
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences


class TestUserPreferences:
    def test_valid_defaults(self):
        prefs = UserPreferences(
            location="btm",
            budget="medium",
            cuisine="italian",
        )
        assert prefs.min_rating == 3.5
        assert prefs.top_k == 5
        assert prefs.location == "Btm"
        assert prefs.additional_preferences is None

    def test_json_round_trip(self):
        prefs = UserPreferences(
            location="Banashankari",
            budget="low",
            cuisine="Chinese",
            min_rating=4.0,
            additional_preferences="family-friendly",
            top_k=3,
        )
        raw = prefs.model_dump_json()
        restored = UserPreferences.model_validate_json(raw)
        assert restored == prefs

    def test_omit_optional_fields_json(self):
        data = {"location": "Btm", "budget": "high", "cuisine": "Thai"}
        prefs = UserPreferences.model_validate_json(json.dumps(data))
        assert prefs.min_rating == 3.5
        assert prefs.top_k == 5
        assert prefs.additional_preferences is None

    def test_reject_empty_location(self):
        with pytest.raises(ValidationError):
            UserPreferences(location="  ", budget="low", cuisine="Chinese")

    def test_reject_empty_cuisine(self):
        with pytest.raises(ValidationError):
            UserPreferences(location="Btm", budget="low", cuisine="")

    def test_reject_invalid_budget(self):
        with pytest.raises(ValidationError):
            UserPreferences.model_validate(
                {"location": "Btm", "budget": "cheap", "cuisine": "Chinese"}
            )

    def test_reject_min_rating_out_of_range(self):
        with pytest.raises(ValidationError):
            UserPreferences(
                location="Btm",
                budget="low",
                cuisine="Chinese",
                min_rating=6.0,
            )

    def test_reject_top_k_out_of_range(self):
        with pytest.raises(ValidationError):
            UserPreferences(
                location="Btm",
                budget="low",
                cuisine="Chinese",
                top_k=0,
            )

    def test_additional_empty_string_becomes_none(self):
        prefs = UserPreferences(
            location="Btm",
            budget="low",
            cuisine="Chinese",
            additional_preferences="   ",
        )
        assert prefs.additional_preferences is None

    def test_mood_accepts_supported_values(self):
        prefs = UserPreferences(
            location="Btm",
            budget="low",
            cuisine="Chinese",
            mood="date_night",
        )
        assert prefs.mood == "date_night"

    def test_mood_rejects_unknown_value(self):
        with pytest.raises(ValidationError):
            UserPreferences(
                location="Btm",
                budget="low",
                cuisine="Chinese",
                mood="party_time",
            )

    def test_sanitize_additional_preferences(self):
        prefs = UserPreferences(
            location="Btm",
            budget="low",
            cuisine="Chinese",
            additional_preferences="<b>quiet</b> place",
        )
        assert prefs.sanitized_additional_preferences(500) == "quiet place"

    def test_to_filter_criteria(self):
        prefs = UserPreferences(
            location="Btm",
            budget="medium",
            cuisine="Italian",
            min_rating=4.2,
        )
        criteria = prefs.to_filter_criteria()
        assert criteria.location == "Btm"
        assert criteria.budget == "medium"
        assert criteria.cuisine == "Italian"
        assert criteria.min_rating == 4.2


class TestRecommendationModels:
    def test_empty_response(self):
        resp = RecommendationResponse()
        assert resp.recommendations == []
        assert resp.summary is None

    def test_response_with_item(self):
        restaurant = Restaurant(
            id="1",
            name="Test",
            location="Btm",
            cuisines=["italian"],
            rating=4.0,
            estimated_cost=800,
            budget_band="medium",
        )
        resp = RecommendationResponse(
            summary="Good picks",
            recommendations=[
                Recommendation(restaurant=restaurant, rank=1, explanation="Nice spot"),
            ],
        )
        data = json.loads(resp.model_dump_json())
        assert data["summary"] == "Good picks"
        assert len(data["recommendations"]) == 1
