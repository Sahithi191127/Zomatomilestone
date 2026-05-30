"""
End-to-end smoke: validate → filter → Groq → recommendations.

  python scripts/recommend_smoke.py --location Btm --budget medium --cuisine italian --min-rating 4.0
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.dependencies import get_recommendation_use_case  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate recommendations via Groq")
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", required=True)
    parser.add_argument("--min-rating", type=float, default=3.5)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--additional", default=None, help="Free-text preferences")
    parser.add_argument("--no-strict-location", action="store_true")
    args = parser.parse_args(argv)

    use_case = get_recommendation_use_case(
        strict_location=not args.no_strict_location,
    )
    response = use_case.execute(
        {
            "location": args.location,
            "budget": args.budget,
            "cuisine": args.cuisine,
            "min_rating": args.min_rating,
            "top_k": args.top_k,
            "additional_preferences": args.additional,
        }
    )

    print(f"Summary: {response.summary}")
    print(f"Fallback used: {response.meta.fallback_used}")
    print(f"Model: {response.meta.llm_model}")
    print(f"Candidates considered: {response.meta.candidates_considered}")
    print(f"Filters: {response.meta.filters_applied}")
    print(f"Recommendations: {len(response.recommendations)}")
    for rec in response.recommendations:
        r = rec.restaurant
        print(f"\n#{rec.rank} {r.name} ({r.location})")
        print(f"   Rating: {r.rating} | Cost: Rs {r.estimated_cost:.0f} | {r.budget_band}")
        print(f"   Cuisines: {', '.join(r.cuisines)}")
        print(f"   {rec.explanation}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
