"""Prompt Builder — Integration Layer (Component Design → 5)."""

from __future__ import annotations

import json

from app.config import settings
from app.models.restaurant import Restaurant
from app.models.user_preferences import UserPreferences
from app.services.context_serializer import build_llm_context

SYSTEM_PROMPT = """You are a restaurant recommendation advisor for a Zomato-style app.

Rules:
- Recommend ONLY from the restaurant list provided in the user message.
- Use ONLY restaurant_id values that appear in that list. Do not invent restaurants.
- Rank by how well each venue matches location, budget, cuisine, minimum rating, mood/occasion, and any additional preferences.
- Mood guidance:
  - date_night: romantic, cozy, quiet, premium ambience
  - family_dinner: family-friendly, spacious, comfortable seating
  - quick_lunch: faster service, practical price, convenience
  - friends_hangout: lively atmosphere, group-friendly setup
  - work_meeting: quieter, professional ambience
  - solo_dining: comfortable for one, calm experience
  - celebration_birthday: party-friendly, festive vibe
  - casual_dining: relaxed, affordable, everyday comfort
  - fine_dining: premium, elegant, high-rated options
  - cafe_chill: coffee/cafe vibe, relaxed ambience
- Return valid JSON only, matching the output schema exactly.
- Provide exactly top_k recommendations (or fewer if fewer candidates exist)."""

OUTPUT_SCHEMA = {
    "summary": "Brief overview of the selection for this user.",
    "recommendations": [
        {
            "restaurant_id": "id from candidate list",
            "rank": 1,
            "explanation": "Why this fits the user's preferences.",
        }
    ],
}


def build_messages(
    preferences: UserPreferences,
    candidates: list[Restaurant],
) -> list[dict[str, str]]:
    """Build chat messages for Groq / OpenAI-compatible APIs."""
    additional = preferences.sanitized_additional_preferences(
        settings.max_additional_preferences_length
    )
    prefs_payload = {
        "location": preferences.location,
        "budget": preferences.budget,
        "cuisine": preferences.cuisine,
        "min_rating": preferences.min_rating,
        "additional_preferences": additional,
        "top_k": preferences.top_k,
        "mood": preferences.mood,
    }
    allowed_ids = [c.id for c in candidates]
    context = build_llm_context(preferences, candidates)

    user_content = (
        f"## User preferences\n{json.dumps(prefs_payload, indent=2)}\n\n"
        f"## Allowed restaurant_id values (use only these)\n{json.dumps(allowed_ids)}\n\n"
        f"## Candidate restaurants\n{json.dumps(context['candidates'], indent=2)}\n\n"
        f"## Task\n"
        f"Rank the top {preferences.top_k} restaurants for this user. "
        f"Return JSON with keys 'summary' and 'recommendations'. "
        f"Each recommendation must have restaurant_id, rank (1..{preferences.top_k}), "
        f"and explanation.\n\n"
        f"## Output schema\n{json.dumps(OUTPUT_SCHEMA, indent=2)}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def allowed_candidate_ids(candidates: list[Restaurant]) -> set[str]:
    return {c.id for c in candidates}
