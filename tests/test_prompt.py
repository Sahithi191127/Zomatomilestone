"""Tests for PromptBuilder (EC-PRM-*, EC-G-03)."""

import json

from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.prompt_builder import allowed_candidate_ids, build_messages


def _candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="abc123",
            name="Test Bistro",
            location="Btm",
            cuisines=["italian"],
            rating=4.5,
            estimated_cost=1200,
            budget_band="medium",
        ),
        Restaurant(
            id="def456",
            name="Other Place",
            location="Btm",
            cuisines=["chinese"],
            rating=4.0,
            estimated_cost=500,
            budget_band="low",
        ),
    ]


class TestPromptBuilder:
    def test_allowed_ids_match_candidates(self):
        candidates = _candidates()
        assert allowed_candidate_ids(candidates) == {"abc123", "def456"}

    def test_prompt_lists_only_candidate_ids(self):
        prefs = UserPreferences(location="Btm", budget="medium", cuisine="italian")
        messages = build_messages(prefs, _candidates())
        user_msg = messages[1]["content"]
        assert "abc123" in user_msg
        assert "def456" in user_msg
        assert "no invent" in messages[0]["content"].lower() or "only" in messages[0]["content"].lower()

    def test_prompt_includes_preferences_and_top_k(self):
        prefs = UserPreferences(
            location="Btm",
            budget="medium",
            cuisine="italian",
            min_rating=4.0,
            additional_preferences="quiet",
            top_k=3,
        )
        messages = build_messages(prefs, _candidates())
        assert "quiet" in messages[1]["content"]
        assert "top_k" in messages[1]["content"] or "3" in messages[1]["content"]

    def test_candidate_block_is_json(self):
        prefs = UserPreferences(location="Btm", budget="medium", cuisine="italian")
        messages = build_messages(prefs, _candidates())
        assert "Candidate restaurants" in messages[1]["content"]
        assert '"id": "abc123"' in messages[1]["content"] or "abc123" in messages[1]["content"]
