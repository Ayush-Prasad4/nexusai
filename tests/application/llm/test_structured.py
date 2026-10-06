import pytest
from pydantic import BaseModel

from app.application.llm.structured import parse_structured_response


class ExampleResult(BaseModel):
    findings: list[str]


def test_parse_structured_response_validates_json() -> None:
    result = parse_structured_response(
        '{"findings": ["Finding one", "Finding two"]}',
        ExampleResult,
    )

    assert result.findings == [
        "Finding one",
        "Finding two",
    ]


def test_parse_structured_response_rejects_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="LLM returned invalid JSON",
    ):
        parse_structured_response(
            "not valid json",
            ExampleResult,
        )


def test_parse_structured_response_rejects_invalid_schema() -> None:
    with pytest.raises(
        ValueError,
        match="LLM response does not match ExampleResult",
    ):
        parse_structured_response(
            '{"findings": "not a list"}',
            ExampleResult,
        )
