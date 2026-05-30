"""
Serialize filtered candidates for Prompt Builder (Phase 4).

Minimal fields per architecture token management guidance.
"""

from __future__ import annotations

import json
from typing import Any

from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences


def serialize_candidates(restaurants: list[Restaurant]) -> list[dict[str, Any]]:
    """Compact candidate records for LLM context."""
    return [
        {
            "id": r.id,
            "name": r.name,
            "location": r.location,
            "cuisines": r.cuisines,
            "rating": r.rating,
            "estimated_cost": r.estimated_cost,
            "budget_band": r.budget_band,
        }
        for r in restaurants
    ]


def build_llm_context(
    preferences: UserPreferences,
    candidates: list[Restaurant],
) -> dict[str, Any]:
    """Preferences summary + candidate block for prompt injection."""
    return {
        "preferences": {
            "location": preferences.location,
            "budget": preferences.budget,
            "cuisine": preferences.cuisine,
            "min_rating": preferences.min_rating,
            "additional_preferences": preferences.additional_preferences,
            "top_k": preferences.top_k,
            "mood": preferences.mood,
        },
        "candidates": serialize_candidates(candidates),
    }


def candidates_to_json(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    *,
    indent: int | None = None,
) -> str:
    return json.dumps(build_llm_context(preferences, candidates), indent=indent)
