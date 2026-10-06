import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_structured_response(
    response: str,
    model: type[ModelT],
) -> ModelT:
    try:
        payload = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON."
        ) from exc

    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(
            f"LLM response does not match {model.__name__}."
        ) from exc
