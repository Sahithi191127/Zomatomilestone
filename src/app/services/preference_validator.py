"""
Preference validation at API / presentation boundary (Component Design → 3).

- Pydantic schema validation for UserPreferences
- Optional location check against repository known locations
- Sanitize / truncate additional_preferences (Cross-Cutting Concerns — Security)
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from app.config import settings
from app.data.repository import RestaurantRepository
from app.exceptions import PreferenceValidationError
from app.models.restaurant import FilterCriteria
from app.models.user_preferences import UserPreferences


def _location_matches(user_location: str, known: str) -> bool:
    user_l = user_location.lower()
    known_l = known.lower()
    return user_l in known_l or known_l in user_l


def suggest_locations(query: str, cities: list[str], *, limit: int = 5) -> list[str]:
    """Return closest known locations for error hints (EC-IN-08 future UX)."""
    q = query.strip().lower()
    if not q:
        return cities[:limit]

    scored: list[tuple[int, str]] = []
    for city in cities:
        cl = city.lower()
        if q == cl:
            return [city]
        if q in cl:
            scored.append((0, city))
        elif cl in q:
            scored.append((1, city))
        elif cl.startswith(q) or q.startswith(cl):
            scored.append((2, city))

    scored.sort(key=lambda item: (item[0], item[1]))
    return [city for _, city in scored[:limit]]


def _format_pydantic_errors(exc: PydanticValidationError) -> PreferenceValidationError:
    errors = exc.errors()
    if not errors:
        return PreferenceValidationError("Invalid preferences")

    first = errors[0]
    loc = first.get("loc", ())
    field = str(loc[-1]) if loc else None
    msg = first.get("msg", "Invalid value")
    if field:
        message = f"{field}: {msg}"
    else:
        message = str(msg)
    return PreferenceValidationError(message, field=field)


class PreferenceValidator:
    """Validate and normalize user preferences before filtering / LLM."""

    def __init__(
        self,
        repository: RestaurantRepository | None = None,
        *,
        strict_location: bool = True,
        max_additional_length: int | None = None,
    ) -> None:
        self._repository = repository
        self._strict_location = strict_location
        self._max_additional_length = (
            max_additional_length or settings.max_additional_preferences_length
        )

    def validate(self, data: dict[str, Any] | UserPreferences) -> UserPreferences:
        """
        Parse, normalize, and validate preferences.

        Raises PreferenceValidationError on invalid input.
        """
        try:
            prefs = (
                data
                if isinstance(data, UserPreferences)
                else UserPreferences.model_validate(data)
            )
        except PydanticValidationError as exc:
            raise _format_pydantic_errors(exc) from exc

        prefs = self._apply_additional_preferences_policy(prefs)

        if self._repository is not None and self._strict_location:
            self._validate_location(prefs)

        return prefs

    def _apply_additional_preferences_policy(self, prefs: UserPreferences) -> UserPreferences:
        if prefs.additional_preferences is None:
            return prefs

        sanitized = prefs.sanitized_additional_preferences(self._max_additional_length)
        if sanitized == prefs.additional_preferences:
            return prefs
        return prefs.model_copy(update={"additional_preferences": sanitized})

    def _validate_location(self, prefs: UserPreferences) -> None:
        cities = self._repository.get_cities()  # type: ignore[union-attr]
        if any(_location_matches(prefs.location, city) for city in cities):
            return

        # Also accept if location-only filter would return rows (substring semantics)
        matches = self._repository.filter(  # type: ignore[union-attr]
            FilterCriteria(location=prefs.location)
        )
        if matches:
            return

        suggestions = suggest_locations(prefs.location, cities)
        hint = ""
        if suggestions:
            hint = f" Did you mean: {', '.join(suggestions[:5])}?"

        raise PreferenceValidationError(
            f"No restaurants found for location '{prefs.location}'.{hint}",
            field="location",
            suggestions=suggestions,
        )


def validate_preferences(
    data: dict[str, Any] | UserPreferences,
    repository: RestaurantRepository | None = None,
    *,
    strict_location: bool = True,
) -> UserPreferences:
    """Convenience wrapper used by API / orchestrator entry points."""
    return PreferenceValidator(repository, strict_location=strict_location).validate(data)
