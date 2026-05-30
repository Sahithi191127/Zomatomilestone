"""Unit tests for SchemaNormalizer / preprocessor (Phase 1)."""

import pandas as pd
import pytest

from app.ingestion.normalizer import (
    _budget_band,
    _parse_cost,
    _parse_cuisines,
    _parse_rating,
    _stable_id,
    normalize_dataframe,
    normalize_row,
)


def _sample_row(**overrides) -> pd.Series:
    base = {
        "name": "Test Bistro",
        "listed_in(city)": "Bangalore",
        "location": "BTM",
        "cuisines": "Italian, Continental",
        "rate": "4.2/5",
        "approx_cost(for two people)": "1,200",
        "votes": 150,
        "address": "123 Main St",
    }
    base.update(overrides)
    return pd.Series(base)


class TestParsingHelpers:
    def test_parse_rating_from_fraction(self):
        assert _parse_rating("4.2/5") == pytest.approx(4.2)

    def test_parse_rating_invalid(self):
        assert _parse_rating("NEW") is None
        assert _parse_rating("-") is None

    def test_parse_cost_with_commas(self):
        assert _parse_cost("1,200") == 1200.0
        assert _parse_cost("300, 400") == 300.0

    def test_parse_cuisines(self):
        assert _parse_cuisines("Italian, Chinese") == ["italian", "chinese"]

    def test_budget_bands(self):
        assert _budget_band(400, 500, 1500) == "low"
        assert _budget_band(800, 500, 1500) == "medium"
        assert _budget_band(2000, 500, 1500) == "high"

    def test_stable_id_deterministic(self):
        assert _stable_id("Foo", "Bar") == _stable_id("Foo", "Bar")
        assert _stable_id("Foo", "Bar") != _stable_id("Foo", "Baz")


class TestNormalizeRow:
    def test_happy_path(self):
        r = normalize_row(_sample_row())
        assert r is not None
        assert r.name == "Test Bistro"
        assert r.location == "Bangalore"
        assert r.rating == pytest.approx(4.2)
        assert r.estimated_cost == 1200.0
        assert r.budget_band == "medium"
        assert "italian" in r.cuisines
        assert r.metadata.get("neighbourhood") == "BTM"
        assert r.metadata.get("votes") == 150

    def test_drops_missing_name(self):
        assert normalize_row(_sample_row(name=None)) is None

    def test_drops_invalid_rating(self):
        assert normalize_row(_sample_row(rate="NEW")) is None

    def test_location_alias_bengaluru(self):
        r = normalize_row(_sample_row(**{"listed_in(city)": "Bengaluru"}))
        assert r is not None
        assert r.location == "Bangalore"

    def test_fallback_neighbourhood_when_no_city(self):
        row = _sample_row()
        row["listed_in(city)"] = None
        row["location"] = "HSR"
        r = normalize_row(row)
        assert r is not None
        assert r.location == "Hsr"


class TestNormalizeDataframe:
    def test_dedupes_by_id_keeps_higher_rating(self):
        df = pd.DataFrame(
            [
                {
                    "name": "Dup Place",
                    "listed_in(city)": "Delhi",
                    "location": "CP",
                    "cuisines": "Chinese",
                    "rate": "3.5/5",
                    "approx_cost(for two people)": "600",
                    "votes": 10,
                },
                {
                    "name": "Dup Place",
                    "listed_in(city)": "Delhi",
                    "location": "CP",
                    "cuisines": "Chinese",
                    "rate": "4.5/5",
                    "approx_cost(for two people)": "600",
                    "votes": 20,
                },
            ]
        )
        result = normalize_dataframe(df)
        assert len(result) == 1
        assert result[0].rating == pytest.approx(4.5)
