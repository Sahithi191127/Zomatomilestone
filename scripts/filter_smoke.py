"""
CLI smoke test: preferences → filtered candidates (no LLM).

  python scripts/filter_smoke.py --location Btm --budget medium --cuisine italian --min-rating 4.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.data.repository import RestaurantRepository  # noqa: E402
from app.models.user_preferences import UserPreferences  # noqa: E402
from app.services.filter_service import FilterService  # noqa: E402
from app.services.preference_validator import validate_preferences  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Filter restaurants by user preferences")
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", required=True)
    parser.add_argument("--min-rating", type=float, default=3.5)
    parser.add_argument("--no-strict-location", action="store_true")
    args = parser.parse_args(argv)

    repo = RestaurantRepository.from_cache()
    prefs = validate_preferences(
        {
            "location": args.location,
            "budget": args.budget,
            "cuisine": args.cuisine,
            "min_rating": args.min_rating,
        },
        repo,
        strict_location=not args.no_strict_location,
    )

    result = FilterService().filter(prefs, repo)

    print(f"Applied filters: {result.applied_filters}")
    print(f"Matches before cap: {result.total_before_cap}")
    print(f"Candidates returned: {len(result.candidates)}")
    for i, r in enumerate(result.candidates[:10], start=1):
        cuisines = ", ".join(r.cuisines[:3])
        print(
            f"  {i}. {r.name} | {r.location} | {r.rating:.1f} | "
            f"{r.budget_band} | {cuisines}"
        )
    if result.is_empty:
        print("No matches — LLM would be skipped in orchestrator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
