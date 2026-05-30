"""Ingestion pipeline: load → normalize → optional persist."""

from __future__ import annotations

import logging
from pathlib import Path

from app.config import settings
from app.ingestion.loader import load_raw_dataset
from app.ingestion.normalizer import normalize_dataframe
from app.ingestion.persistence import read_parquet, write_parquet
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


def ingest_from_hf() -> list[Restaurant]:
    """Fetch from Hugging Face, normalize, return canonical restaurants."""
    logger.info("Loading dataset %s from Hugging Face...", settings.hf_dataset_name)
    raw_df = load_raw_dataset()
    logger.info("Raw rows: %d", len(raw_df))
    restaurants = normalize_dataframe(raw_df)
    logger.info("Normalized restaurants: %d", len(restaurants))
    return restaurants


def ingest_and_persist(output_path: Path | None = None) -> list[Restaurant]:
    """Ingest from HF, write Parquet cache, return restaurants."""
    path = output_path or settings.data_path
    restaurants = ingest_from_hf()
    write_parquet(restaurants, path)
    logger.info("Wrote %d restaurants to %s", len(restaurants), path)
    return restaurants


def load_restaurants(path: Path | None = None, *, refresh: bool = False) -> list[Restaurant]:
    """
    Load restaurants from Parquet cache, or ingest from HF if missing or refresh=True.
    """
    path = path or settings.data_path
    if refresh or not path.exists():
        return ingest_and_persist(path)
    logger.info("Loading restaurants from cache: %s", path)
    return read_parquet(path)
