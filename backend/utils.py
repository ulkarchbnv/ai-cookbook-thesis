import ast
import json
from typing import Any


def load_serialized_value(raw_value: str | None, fallback: Any) -> Any:
    if raw_value is None:
        return fallback

    try:
        return json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        try:
            return ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            return fallback


def load_serialized_list(raw_value: str | None) -> list[str]:
    value = load_serialized_value(raw_value, [])
    return value if isinstance(value, list) else []
