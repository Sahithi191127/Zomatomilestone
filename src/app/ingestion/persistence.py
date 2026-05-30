"""PersistenceWriter — save/load processed restaurants as Parquet."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.models.restaurant import Restaurant


def _restaurants_to_frame(restaurants: list[Restaurant]) -> pd.DataFrame:
    records = []
    for r in restaurants:
        records.append(
            {
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": json.dumps(r.cuisines),
                "rating": r.rating,
                "estimated_cost": r.estimated_cost,
                "budget_band": r.budget_band,
                "metadata": json.dumps(r.metadata),
            }
        )
    return pd.DataFrame.from_records(records)


def _frame_to_restaurants(df: pd.DataFrame) -> list[Restaurant]:
    restaurants: list[Restaurant] = []
    for _, row in df.iterrows():
        cuisines = json.loads(row["cuisines"]) if isinstance(row["cuisines"], str) else row["cuisines"]
        metadata = json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"]
        restaurants.append(
            Restaurant(
                id=str(row["id"]),
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=list(cuisines),
                rating=float(row["rating"]),
                estimated_cost=float(row["estimated_cost"]),
                budget_band=row["budget_band"],
                metadata=dict(metadata) if metadata else {},
            )
        )
    return restaurants


def write_parquet(restaurants: list[Restaurant], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = _restaurants_to_frame(restaurants)
    frame.to_parquet(path, index=False)


def read_parquet(path: Path) -> list[Restaurant]:
    if not path.exists():
        raise FileNotFoundError(f"Processed data not found: {path}")
    df = pd.read_parquet(path)
    return _frame_to_restaurants(df)
