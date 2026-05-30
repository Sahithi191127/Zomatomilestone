"""
SchemaNormalizer + Preprocessor — map HF rows to canonical Restaurant.

Column mapping (ManikaSaini/zomato-restaurant-recommendation):
  name                          -> name
  listed_in(city)               -> location (city for user filters; fallback: location)
  location                      -> metadata.neighbourhood
  cuisines                      -> cuisines (comma-separated -> list[str])
  approx_cost(for two people)   -> estimated_cost (parse numeric string)
  rate                          -> rating (parse "4.1/5"; invalid -> drop row)
  votes                         -> metadata.votes
  address, rest_type, ...       -> metadata
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

import pandas as pd

from app.config import settings
from app.models.restaurant import BudgetBand, Restaurant

# City aliases for consistent filtering (EC-ING-08)
LOCATION_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "gurugram": "Gurgaon",
    "gurgaon": "Gurgaon",
}

_RATE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)")
_COST_DIGITS = re.compile(r"\d+")


def _stable_id(name: str, location: str) -> str:
    key = f"{name.strip().lower()}|{location.strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _title_location(raw: str) -> str:
    stripped = raw.strip()
    if not stripped:
        return stripped
    key = stripped.lower()
    if key in LOCATION_ALIASES:
        return LOCATION_ALIASES[key]
    return stripped.title()


def _parse_rating(rate_val: Any) -> float | None:
    if rate_val is None or (isinstance(rate_val, float) and pd.isna(rate_val)):
        return None
    text = str(rate_val).strip()
    if not text or text.upper() in {"NEW", "-", "NAN"}:
        return None
    match = _RATE_PATTERN.search(text)
    if not match:
        return None
    value = float(match.group(1))
    return max(0.0, min(5.0, value))


def _parse_cost(cost_val: Any) -> float | None:
    if cost_val is None or (isinstance(cost_val, float) and pd.isna(cost_val)):
        return None
    text = str(cost_val).strip().lower()
    if not text or text in {"-", "nan"}:
        return None
    digits = _COST_DIGITS.findall(text.replace(",", ""))
    if not digits:
        return None
    # Use first number when range like "300, 400" or "1,200"
    return float(digits[0])


def _parse_cuisines(raw: Any) -> list[str]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return []
    parts = [p.strip().lower() for p in str(raw).split(",") if p.strip()]
    return parts


def _budget_band(cost: float, low_max: float, medium_max: float) -> BudgetBand:
    if cost <= low_max:
        return "low"
    if cost <= medium_max:
        return "medium"
    return "high"


def _resolve_city(row: pd.Series) -> str:
    city = row.get("listed_in(city)")
    if city is not None and not (isinstance(city, float) and pd.isna(city)):
        city_str = str(city).strip()
        if city_str:
            return _title_location(city_str)
    neighbourhood = row.get("location")
    if neighbourhood is not None and not (isinstance(neighbourhood, float) and pd.isna(neighbourhood)):
        nb = str(neighbourhood).strip()
        if nb:
            return _title_location(nb)
    return ""


def _build_metadata(row: pd.Series) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    optional_fields = (
        "address",
        "url",
        "phone",
        "rest_type",
        "dish_liked",
        "online_order",
        "book_table",
        "listed_in(type)",
    )
    for field in optional_fields:
        val = row.get(field)
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            meta[field.replace("(", "_").replace(")", "")] = val

    neighbourhood = row.get("location")
    if neighbourhood is not None and not (isinstance(neighbourhood, float) and pd.isna(neighbourhood)):
        meta["neighbourhood"] = str(neighbourhood).strip()

    votes = row.get("votes")
    if votes is not None and not (isinstance(votes, float) and pd.isna(votes)):
        try:
            meta["votes"] = int(votes)
        except (TypeError, ValueError):
            pass

    return meta


def normalize_row(row: pd.Series) -> Restaurant | None:
    """Map one HF row to Restaurant, or None if row should be dropped."""
    name_val = row.get("name")
    if name_val is None or (isinstance(name_val, float) and pd.isna(name_val)):
        return None
    name = str(name_val).strip()
    if not name:
        return None

    location = _resolve_city(row)
    if not location:
        return None

    rating = _parse_rating(row.get("rate"))
    if rating is None:
        return None

    cost = _parse_cost(row.get("approx_cost(for two people)"))
    if cost is None or cost <= 0:
        return None

    cuisines = _parse_cuisines(row.get("cuisines"))
    band = _budget_band(cost, settings.budget_low_max, settings.budget_medium_max)

    return Restaurant(
        id=_stable_id(name, location),
        name=name,
        location=location,
        cuisines=cuisines,
        rating=rating,
        estimated_cost=cost,
        budget_band=band,
        metadata=_build_metadata(row),
    )


def normalize_dataframe(df: pd.DataFrame) -> list[Restaurant]:
    """Normalize all rows, dedupe by id (keep highest rating), return restaurants."""
    by_id: dict[str, Restaurant] = {}

    for _, row in df.iterrows():
        restaurant = normalize_row(row)
        if restaurant is None:
            continue
        existing = by_id.get(restaurant.id)
        if existing is None or restaurant.rating > existing.rating:
            by_id[restaurant.id] = restaurant

    return list(by_id.values())
