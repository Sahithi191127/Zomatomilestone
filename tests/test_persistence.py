"""Parquet round-trip tests."""

from pathlib import Path

import pytest

from app.ingestion.persistence import read_parquet, write_parquet
from app.models.restaurant import Restaurant


@pytest.fixture
def sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="abc",
            name="Cache Test",
            location="Mumbai",
            cuisines=["thai"],
            rating=4.1,
            estimated_cost=900,
            budget_band="medium",
            metadata={"votes": 42},
        )
    ]


def test_parquet_round_trip(tmp_path: Path, sample_restaurants: list[Restaurant]):
    path = tmp_path / "restaurants.parquet"
    write_parquet(sample_restaurants, path)
    loaded = read_parquet(path)
    assert len(loaded) == 1
    assert loaded[0].id == "abc"
    assert loaded[0].cuisines == ["thai"]
    assert loaded[0].metadata["votes"] == 42
