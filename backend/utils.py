import ast
import hashlib
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


def build_recipe_fingerprint(
    title: str,
    ingredients: list[str],
    preferences: list[str],
    allergies: list[str],
    steps: list[str],
) -> str:
    normalized_payload = {
        "title": " ".join(title.strip().lower().split()),
        "ingredients": sorted(" ".join(item.strip().lower().split()) for item in ingredients if item.strip()),
        "preferences": sorted(" ".join(item.strip().lower().split()) for item in preferences if item.strip()),
        "allergies": sorted(" ".join(item.strip().lower().split()) for item in allergies if item.strip()),
        "steps": [" ".join(step.strip().split()) for step in steps if step.strip()],
    }
    serialized = json.dumps(normalized_payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
