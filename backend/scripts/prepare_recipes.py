import argparse
import csv
import html
import json
import re
from pathlib import Path


DEFAULT_INPUT_PATH = Path("backend/data/recipes_ingredients.csv")
DEFAULT_OUTPUT_PATH = Path("backend/data/recipes_subset.json")
DEFAULT_LIMIT = 10_000
DEFAULT_SOURCE = "Food.com Kaggle dataset"


def normalize_text(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[\u2018\u2019]", "'", cleaned)
    cleaned = re.sub(r"[\u201c\u201d]", '"', cleaned)
    cleaned = re.sub(r"[^a-z0-9\s'/-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" -_/")


def clean_display_text(value: str) -> str:
    cleaned = html.unescape(value).replace("Â", "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def parse_json_list(raw_value: str) -> list[str]:
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    cleaned_items: list[str] = []
    for item in parsed:
        if not isinstance(item, str):
            continue
        text = clean_display_text(item)
        if text:
            cleaned_items.append(text)
    return cleaned_items


def normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        candidate = normalize_text(tag.replace("_", " ").replace("-", " "))
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)

    return normalized


def clean_ingredients(ingredients: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for ingredient in ingredients:
        display_text = clean_display_text(ingredient)
        normalized_text = normalize_text(display_text)
        if not normalized_text or normalized_text in seen:
            continue
        seen.add(normalized_text)
        normalized.append(normalized_text)

    return normalized


def clean_steps(steps: list[str]) -> list[str]:
    cleaned_steps: list[str] = []

    for step in steps:
        display_text = clean_display_text(step)
        if not display_text:
            continue
        if len(normalize_text(display_text)) < 5:
            continue
        cleaned_steps.append(display_text)

    return cleaned_steps


def build_instruction_summary(steps: list[str], max_steps: int = 3, max_chars: int = 280) -> str:
    summary_parts: list[str] = []

    for step in steps[:max_steps]:
        cleaned = clean_display_text(step)
        cleaned = re.sub(r"\s*\([^)]*\)", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
        if cleaned:
            summary_parts.append(cleaned)

    summary = " ".join(summary_parts)
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3].rstrip() + "..."

    return summary


def build_duplicate_key(title: str, ingredients: list[str]) -> str:
    normalized_title = normalize_text(title)
    sorted_ingredients = sorted(ingredients)
    return "|".join([normalized_title, *sorted_ingredients])


def is_valid_recipe(title: str, ingredients: list[str], steps: list[str], summary: str) -> bool:
    if not clean_display_text(title):
        return False
    if len(ingredients) < 2:
        return False
    if len(steps) < 1:
        return False
    if len(normalize_text(summary)) < 10:
        return False
    return True


def prepare_recipes(
    input_path: Path,
    output_path: Path,
    limit: int,
) -> dict[str, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    seen_duplicates: set[str] = set()
    stats = {
        "rows_read": 0,
        "rows_kept": 0,
        "duplicates_skipped": 0,
        "invalid_skipped": 0,
    }

    with input_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            stats["rows_read"] += 1

            title = clean_display_text(row.get("name", ""))
            ingredients = clean_ingredients(parse_json_list(row.get("ingredients", "[]")))
            steps = clean_steps(parse_json_list(row.get("steps", "[]")))
            tags = normalize_tags(parse_json_list(row.get("tags", "[]")))
            summary = build_instruction_summary(steps)

            if not is_valid_recipe(title, ingredients, steps, summary):
                stats["invalid_skipped"] += 1
                continue

            duplicate_key = build_duplicate_key(title, ingredients)
            if duplicate_key in seen_duplicates:
                stats["duplicates_skipped"] += 1
                continue

            seen_duplicates.add(duplicate_key)

            results.append(
                {
                    "recipe_id": str(row.get("id", "")).strip(),
                    "title": title,
                    "ingredients": ingredients,
                    "tags": tags,
                    "steps": steps,
                    "instruction_summary": summary,
                    "minutes": None,
                    "source": DEFAULT_SOURCE,
                }
            )
            stats["rows_kept"] += 1

            if len(results) >= limit:
                break

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(results, output_file, ensure_ascii=False, indent=2)

    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean the raw recipe dataset into a RAG-ready recipe subset."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = prepare_recipes(
        input_path=args.input,
        output_path=args.output,
        limit=args.limit,
    )

    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Rows read: {stats['rows_read']}")
    print(f"Rows kept: {stats['rows_kept']}")
    print(f"Invalid rows skipped: {stats['invalid_skipped']}")
    print(f"Duplicate rows skipped: {stats['duplicates_skipped']}")


if __name__ == "__main__":
    main()
