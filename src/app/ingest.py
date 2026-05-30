"""CLI entry: python -m app.ingest"""

from __future__ import annotations

import argparse
import logging
import sys

from app.data.repository import RestaurantRepository
from app.ingestion.pipeline import ingest_and_persist, load_restaurants

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest Zomato dataset from Hugging Face")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download and re-process even if Parquet cache exists",
    )
    args = parser.parse_args(argv)

    if args.refresh:
        restaurants = ingest_and_persist()
    else:
        restaurants = load_restaurants(refresh=False)

    repo = RestaurantRepository(restaurants)
    cities = repo.get_cities()
    cuisines = repo.get_cuisines()

    logger.info("Total restaurants: %d", len(repo))
    logger.info("Distinct cities: %d (sample: %s)", len(cities), cities[:8])
    logger.info("Distinct cuisine tags: %d", len(cuisines))

    major = ("Delhi", "Bangalore", "Mumbai", "Hyderabad", "Chennai", "Kolkata", "Pune")
    for city in major:
        count = sum(1 for r in restaurants if r.location == city)
        if count:
            logger.info("  %s: %d restaurants", city, count)

    if restaurants:
        sample = restaurants[0]
        logger.info(
            "Sample: id=%s name=%r location=%s rating=%.1f cost=%.0f band=%s cuisines=%s",
            sample.id,
            sample.name,
            sample.location,
            sample.rating,
            sample.estimated_cost,
            sample.budget_band,
            sample.cuisines[:3],
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
