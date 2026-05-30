"""RestaurantRepository — read access to preprocessed restaurants."""

from __future__ import annotations

from pathlib import Path

from app.ingestion.pipeline import load_restaurants
from app.models.restaurant import FilterCriteria, Restaurant


class RestaurantRepository:
    def __init__(self, restaurants: list[Restaurant] | None = None) -> None:
        self._restaurants: list[Restaurant] = restaurants or []
        self._by_id: dict[str, Restaurant] = {r.id: r for r in self._restaurants}

    @classmethod
    def from_cache(cls, path: Path | None = None, *, refresh: bool = False) -> RestaurantRepository:
        restaurants = load_restaurants(path, refresh=refresh)
        return cls(restaurants)

    def load(self, *, refresh: bool = False, path: Path | None = None) -> None:
        """Load or reload data into the repository."""
        self._restaurants = load_restaurants(path, refresh=refresh)
        self._by_id = {r.id: r for r in self._restaurants}

    def get_all(self) -> list[Restaurant]:
        return list(self._restaurants)

    def get_by_ids(self, ids: list[str]) -> list[Restaurant]:
        return [self._by_id[i] for i in ids if i in self._by_id]

    def get_cities(self) -> list[str]:
        cities = sorted({r.location for r in self._restaurants if r.location})
        return cities

    def get_cuisines(self) -> list[str]:
        tags: set[str] = set()
        for r in self._restaurants:
            tags.update(r.cuisines)
        return sorted(tags)

    def filter(self, criteria: FilterCriteria) -> list[Restaurant]:
        results = self._restaurants

        if criteria.location:
            loc = criteria.location.strip().lower()
            results = [r for r in results if loc in r.location.lower()]

        if criteria.budget:
            results = [r for r in results if r.budget_band == criteria.budget]

        if criteria.cuisine:
            needle = criteria.cuisine.strip().lower()
            results = [
                r
                for r in results
                if any(needle in c or c in needle for c in r.cuisines)
            ]

        if criteria.min_rating is not None:
            results = [r for r in results if r.rating >= criteria.min_rating]

        return results

    def __len__(self) -> int:
        return len(self._restaurants)
