#!/usr/bin/env python3
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "meta.version",
    "meta.created_by",
    "meta.content_language",
    "project.name",
    "project.summary",
    "project.task_type",
    "audience.primary_user",
    "goals.business_goal",
    "goals.design_goal",
    "message.core_claim",
    "structure.sections",
    "visual.strategy_name",
    "design_system.design_md_path",
    "quality_bar.review_criteria",
]

SUPPORTED_CONTENT_LANGUAGES = {"zh-CN"}


def value_at(data, dotted_path):
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def resolve_existing_path(raw_path, brief_path):
    candidate = Path(str(raw_path)).expanduser()
    candidates = [candidate] if candidate.is_absolute() else [
        brief_path.parent / candidate,
        Path.cwd() / candidate,
    ]
    for entry in candidates:
        if entry.exists():
            return entry
    return None


def main(argv):
    if len(argv) != 2:
        print("usage: validate_brief.py <brief.json>", file=sys.stderr)
        return 1

    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"missing file: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid json: {exc}", file=sys.stderr)
        return 1

    missing = [field for field in REQUIRED_FIELDS if not has_value(value_at(data, field))]
    if missing:
        print("missing fields:")
        for field in missing:
            print(f"- {field}")
        return 1

    content_language = value_at(data, "meta.content_language")
    if content_language not in SUPPORTED_CONTENT_LANGUAGES:
        print("invalid references:")
        print(f"- meta.content_language must be one of: {', '.join(sorted(SUPPORTED_CONTENT_LANGUAGES))}")
        return 1

    if not has_value(data.get("assumptions")) and not has_value(data.get("open_questions")):
        print("missing fields:")
        print("- assumptions or open_questions")
        return 1

    design_md_path = value_at(data, "design_system.design_md_path")
    if not resolve_existing_path(design_md_path, path):
        print("invalid references:")
        print(f"- design_system.design_md_path does not exist: {design_md_path}")
        return 1

    print(f"valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
