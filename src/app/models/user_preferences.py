"""User input model (Component Design → 3. User Input Module)."""

from __future__ import annotations

import re
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.restaurant import BudgetBand, FilterCriteria

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_HTML_TAG = re.compile(r"<[^>]+>")
MoodType = (
    str
)  # Alias kept simple for payload compatibility and easier UI->API mapping.
ALLOWED_MOODS = {
    "date_night",
    "family_dinner",
    "quick_lunch",
    "friends_hangout",
    "work_meeting",
    "solo_dining",
    "celebration_birthday",
    "casual_dining",
    "fine_dining",
    "cafe_chill",
}


class UserPreferences(BaseModel):
    location: str
    budget: BudgetBand
    cuisine: str
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0)
    additional_preferences: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    mood: MoodType | None = None

    @field_validator("location", "cuisine", mode="before")
    @classmethod
    def reject_empty_required_strings(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field is required")
        if isinstance(value, str) and not value.strip():
            raise ValueError("Must not be empty")
        return value

    @field_validator("location", "cuisine", mode="after")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()

    @field_validator("additional_preferences", mode="before")
    @classmethod
    def empty_additional_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("mood", mode="before")
    @classmethod
    def normalize_mood(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Mood must be a string")
        mood = value.strip().lower()
        if not mood:
            return None
        if mood not in ALLOWED_MOODS:
            allowed = ", ".join(sorted(ALLOWED_MOODS))
            raise ValueError(f"Unsupported mood. Allowed values: {allowed}")
        return mood

    @model_validator(mode="after")
    def normalize_display_fields(self) -> Self:
        object.__setattr__(self, "location", self.location.strip().title())
        object.__setattr__(self, "cuisine", self.cuisine.strip())
        return self

    def to_filter_criteria(self) -> FilterCriteria:
        """Map user preferences to repository filter dimensions."""
        return FilterCriteria(
            location=self.location,
            budget=self.budget,
            cuisine=self.cuisine,
            min_rating=self.min_rating,
        )

    def sanitized_additional_preferences(self, max_length: int) -> str | None:
        """Return sanitized free-text preferences for LLM (truncated if needed)."""
        if self.additional_preferences is None:
            return None
        text = _CONTROL_CHARS.sub("", self.additional_preferences)
        text = _HTML_TAG.sub("", text).strip()
        if not text:
            return None
        if len(text) > max_length:
            return text[:max_length]
        return text
