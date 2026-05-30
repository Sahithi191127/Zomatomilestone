"""Tests for ResponseParser (EC-LLM-*)."""

import pytest

from app.services.response_parser import (
    ResponseParseError,
    extract_json_block,
    parse_llm_response,
)


def _valid_json(extra_id: bool = False) -> str:
    recs = [
        {
            "restaurant_id": "id1",
            "rank": 1,
            "explanation": "Great Italian spot in Btm.",
        },
        {
            "restaurant_id": "id2",
            "rank": 2,
            "explanation": "Solid backup option.",
        },
    ]
    if extra_id:
        recs.append(
            {
                "restaurant_id": "hallucinated",
                "rank": 3,
                "explanation": "Fake place.",
            }
        )
    import json

    return json.dumps(
        {
            "summary": "Two strong Italian options.",
            "recommendations": recs,
        }
    )


class TestResponseParser:
    def test_parse_valid_response(self):
        parsed = parse_llm_response(_valid_json(), {"id1", "id2"}, top_k=5)
        assert parsed.summary == "Two strong Italian options."
        assert len(parsed.recommendations) == 2
        assert parsed.recommendations[0].restaurant_id == "id1"

    def test_rejects_hallucinated_id_ec_llm_03(self):
        parsed = parse_llm_response(_valid_json(extra_id=True), {"id1", "id2"}, top_k=5)
        assert len(parsed.recommendations) == 2
        assert all(r.restaurant_id in {"id1", "id2"} for r in parsed.recommendations)

    def test_invalid_json_raises(self):
        with pytest.raises(ResponseParseError):
            parse_llm_response("not json at all", {"id1"})

    def test_extract_json_from_markdown_fence(self):
        raw = 'Here is the result:\n```json\n{"summary": "Hi", "recommendations": [{"restaurant_id": "id1", "rank": 1, "explanation": "x"}]}\n```'
        block = extract_json_block(raw)
        parsed = parse_llm_response(block, {"id1"})
        assert parsed.recommendations[0].restaurant_id == "id1"

    def test_duplicate_ranks_dropped(self):
        import json

        raw = json.dumps(
            {
                "summary": "Ok",
                "recommendations": [
                    {"restaurant_id": "id1", "rank": 1, "explanation": "a"},
                    {"restaurant_id": "id2", "rank": 1, "explanation": "b"},
                ],
            }
        )
        parsed = parse_llm_response(raw, {"id1", "id2"})
        assert len(parsed.recommendations) == 1

    def test_empty_valid_list_raises(self):
        import json

        raw = json.dumps({"summary": "x", "recommendations": []})
        with pytest.raises(ResponseParseError):
            parse_llm_response(raw, {"id1"})
