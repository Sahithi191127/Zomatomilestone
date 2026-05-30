"""Parse and validate LLM JSON output."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")


class ParsedRecommendation(BaseModel):
    restaurant_id: str
    rank: int = Field(ge=1)
    explanation: str


class ParsedLLMResponse(BaseModel):
    summary: str | None = None
    recommendations: list[ParsedRecommendation] = Field(default_factory=list)


class ResponseParseError(Exception):
    pass


def extract_json_block(text: str) -> str:
    """Try raw parse first, then regex extract outermost JSON object."""
    stripped = text.strip()
    if stripped.startswith("{"):
        return stripped
    match = _JSON_BLOCK.search(text)
    if not match:
        raise ResponseParseError("No JSON object found in LLM response")
    return match.group(0)


def parse_llm_response(
    raw: str,
    allowed_ids: set[str],
    *,
    top_k: int | None = None,
) -> ParsedLLMResponse:
    """
    Parse LLM JSON and validate restaurant_id membership.

    Drops unknown ids and duplicate ranks; keeps valid entries sorted by rank.
    """
    try:
        payload: dict[str, Any] = json.loads(extract_json_block(raw))
    except (json.JSONDecodeError, ResponseParseError) as exc:
        raise ResponseParseError(f"Invalid JSON: {exc}") from exc

    summary = payload.get("summary")
    if summary is not None:
        summary = str(summary).strip() or None

    raw_recs = payload.get("recommendations")
    if not isinstance(raw_recs, list):
        raise ResponseParseError("Missing or invalid 'recommendations' array")

    seen_ranks: set[int] = set()
    valid: list[ParsedRecommendation] = []

    for item in raw_recs:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("restaurant_id", "")).strip()
        if rid not in allowed_ids:
            continue
        try:
            rank = int(item.get("rank", 0))
            explanation = str(item.get("explanation", "")).strip()
        except (TypeError, ValueError):
            continue
        if rank < 1 or rank in seen_ranks or not explanation:
            continue
        seen_ranks.add(rank)
        valid.append(
            ParsedRecommendation(
                restaurant_id=rid,
                rank=rank,
                explanation=explanation,
            )
        )

    valid.sort(key=lambda r: r.rank)
    if top_k is not None:
        valid = valid[:top_k]

    if not valid:
        raise ResponseParseError("No valid recommendations after validation")

    return ParsedLLMResponse(summary=summary, recommendations=valid)
