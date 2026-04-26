#!/usr/bin/env python3
import json
import sys
from pathlib import Path


TARGET_TOOLS = {"huashu-design", "claude-design", "v0", "generic"}
EVIDENCE_KINDS = {"pasted_summary", "local_file", "screenshot_reference", "gstack_report"}
DECISIONS = {"accept", "tweak", "revise_brief_then_regenerate", "regenerate_from_scratch"}
PROMPT_INTENTS = {"targeted_modification", "brief_revision_regeneration", "full_regeneration"}
DECISION_PROMPT_INTENTS = {
    "tweak": "targeted_modification",
    "revise_brief_then_regenerate": "brief_revision_regeneration",
    "regenerate_from_scratch": "full_regeneration",
}
VISUAL_STATUSES = {"available_model_image", "available_gstack", "not_provided", "unavailable"}
SEVERITIES = {"low", "medium", "high"}
LOCAL_FILE_SUFFIXES = {".txt", ".md", ".html", ".json"}


def repo_root():
    return Path(__file__).resolve().parents[1]


def value_at(data, dotted_path):
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def has_non_empty_list(value):
    return isinstance(value, list) and bool(value)


def validate_text_list(value, field_name, errors):
    if not isinstance(value, list) or not value:
        errors.append(f"{field_name} must be a non-empty array for non-accept decisions")
        return
    for index, item in enumerate(value):
        if not has_text(item):
            errors.append(f"{field_name}[{index}] must be non-empty text")


def resolve_existing_path(raw_path, bases):
    if not has_text(raw_path):
        return None
    candidate = Path(raw_path).expanduser()
    candidates = [candidate] if candidate.is_absolute() else [base / candidate for base in bases]
    for entry in candidates:
        if entry.is_file():
            return entry.resolve()
    return None


def describe_bases(bases):
    return ", ".join(str(base) for base in bases)


def load_json(path, errors, label):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{label} missing file: {path}")
    except UnicodeDecodeError as exc:
        errors.append(f"{label} is not readable UTF-8 text: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"{label} invalid json: {exc}")
    except OSError as exc:
        errors.append(f"{label} cannot be read: {exc}")
    return {}


def load_json_object(path, errors, label):
    before = len(errors)
    data = load_json(path, errors, label)
    if len(errors) != before:
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label} must be a JSON object")
        return {}
    return data


def selected_strategy(brief):
    if not isinstance(brief, dict):
        return ""
    strategy = value_at(brief, "visual.strategy_name")
    if has_text(strategy):
        return strategy.strip()
    options = brief.get("strategy_options", [])
    if not isinstance(options, list):
        return ""
    for item in options:
        if isinstance(item, dict) and item.get("selected") and has_text(item.get("name")):
            return item["name"].strip()
    return ""


def validate_findings(data, errors):
    decision = data.get("decision")
    findings = data.get("findings")
    if decision == "accept":
        return
    if not isinstance(findings, list) or not findings:
        errors.append("findings must be a non-empty array for non-accept decisions")
        return
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"{prefix}.severity must be one of {sorted(SEVERITIES)}")
        for field in ["brief_reference", "issue", "evidence", "recommended_change"]:
            if not has_text(finding.get(field)):
                errors.append(f"{prefix}.{field} is required")


def validate_prompt(data, errors):
    decision = data.get("decision")
    prompt_intent = data.get("prompt_intent")
    if decision == "accept":
        if has_text(prompt_intent):
            errors.append("prompt_intent must be omitted or blank when decision is accept")
        return

    expected = DECISION_PROMPT_INTENTS.get(decision)
    if has_text(prompt_intent) and prompt_intent not in PROMPT_INTENTS:
        errors.append(f"prompt_intent must be one of {sorted(PROMPT_INTENTS)}")
    if expected and prompt_intent != expected:
        errors.append(f"prompt_intent must be {expected} when decision is {decision}")

    prompt = data.get("prompt")
    if not isinstance(prompt, dict):
        errors.append("prompt is required for non-accept decisions")
        return
    for field in ["keep", "change", "acceptance_checks"]:
        validate_text_list(prompt.get(field), f"prompt.{field}", errors)


def validate_visual(data, errors):
    evidence = data.get("evidence") if isinstance(data.get("evidence"), dict) else {}
    visual = data.get("visual_review") if isinstance(data.get("visual_review"), dict) else {}
    kind = evidence.get("kind")
    status = visual.get("status")

    if status not in VISUAL_STATUSES:
        errors.append(f"visual_review.status must be one of {sorted(VISUAL_STATUSES)}")
        return
    if not has_text(visual.get("notes")):
        errors.append("visual_review.notes is required")
    if status in {"available_model_image", "available_gstack"} and not has_text(visual.get("source")):
        errors.append("visual_review.source is required when visual review is available")
    if kind == "gstack_report":
        if status != "available_gstack":
            errors.append("visual_review.status must be available_gstack when evidence.kind is gstack_report")
        if not has_text(visual.get("source")):
            errors.append("visual_review.source is required for gstack_report evidence")
    if kind == "screenshot_reference":
        has_source = has_text(evidence.get("path")) or has_text(visual.get("source"))
        if not has_source:
            errors.append("screenshot_reference requires evidence.path or visual_review.source")
        if status not in {"available_model_image", "unavailable"}:
            errors.append("screenshot_reference requires available_model_image or unavailable visual status")
    if kind in {"screenshot_reference", "gstack_report"} and status == "not_provided":
        errors.append("visual_review.status not_provided cannot be used with visual evidence")


def validate_review(path):
    review_path = Path(path)
    errors = []
    data = load_json_object(review_path, errors, "review")
    if errors:
        return data, {}, errors

    if not has_text(data.get("schema_version")) or not str(data.get("schema_version")).startswith("1"):
        errors.append("schema_version must be a string starting with 1")

    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source is required")
        source = {}

    brief_bases = [
        review_path.parent,
        review_path.parent.parent,
        Path.cwd(),
        repo_root(),
    ]
    brief_path = resolve_existing_path(source.get("brief_path"), brief_bases)
    if not brief_path:
        errors.append(f"source.brief_path does not resolve: {source.get('brief_path')} (tried bases: {describe_bases(brief_bases)})")
        brief = {}
    else:
        brief = load_json_object(brief_path, errors, "source.brief_path")

    design_bases = [
        brief_path.parent if brief_path else review_path.parent.parent,
        review_path.parent,
        review_path.parent.parent,
        Path.cwd(),
        repo_root(),
    ]
    review_design_path = resolve_existing_path(source.get("design_md_path"), design_bases)
    if not review_design_path:
        errors.append(f"source.design_md_path does not resolve: {source.get('design_md_path')} (tried bases: {describe_bases(design_bases)})")

    brief_design_raw = value_at(brief, "design_system.design_md_path")
    brief_design_path = resolve_existing_path(brief_design_raw, design_bases)
    if not brief_design_path:
        errors.append(f"design_system.design_md_path does not resolve: {brief_design_raw} (tried bases: {describe_bases(design_bases)})")
    elif review_design_path and review_design_path != brief_design_path:
        errors.append("source.design_md_path must match design_system.design_md_path")

    if data.get("target_tool") not in TARGET_TOOLS:
        errors.append(f"target_tool must be one of {sorted(TARGET_TOOLS)}")

    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence is required")
        evidence = {}
    kind = evidence.get("kind")
    if kind not in EVIDENCE_KINDS:
        errors.append(f"evidence.kind must be one of {sorted(EVIDENCE_KINDS)}")
    if not has_text(evidence.get("summary")):
        errors.append("evidence.summary is required")
    if kind == "local_file":
        local_bases = [
            review_path.parent,
            brief_path.parent if brief_path else review_path.parent.parent,
            Path.cwd(),
            repo_root(),
        ]
        local_path = resolve_existing_path(evidence.get("path"), local_bases)
        if not has_text(evidence.get("path")):
            errors.append("evidence.path is required when evidence.kind is local_file")
        elif not local_path:
            errors.append(f"evidence.path does not resolve: {evidence.get('path')} (tried bases: {describe_bases(local_bases)})")
        elif local_path.suffix not in LOCAL_FILE_SUFFIXES:
            errors.append(f"evidence.path has unsupported suffix: {local_path.suffix}")
        else:
            try:
                local_text = local_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"evidence.path must be readable UTF-8 text: {evidence.get('path')} ({exc})")
            else:
                if not local_text.strip():
                    errors.append("evidence.path must contain non-whitespace content")

    decision = data.get("decision")
    if decision not in DECISIONS:
        errors.append(f"decision must be one of {sorted(DECISIONS)}")

    if not has_text(data.get("selected_strategy")):
        errors.append("selected_strategy is required")
    strategy_preserved = data.get("strategy_preserved")
    if not isinstance(strategy_preserved, bool):
        errors.append("strategy_preserved must be a boolean")
    elif strategy_preserved:
        source_strategy = selected_strategy(brief)
        if not source_strategy:
            errors.append("source brief must define selected strategy when strategy_preserved is true")
        elif data.get("selected_strategy") != source_strategy:
            errors.append("selected_strategy must match the source brief when strategy_preserved is true")
    else:
        if decision not in {"revise_brief_then_regenerate", "regenerate_from_scratch"}:
            errors.append("strategy_preserved false is only allowed for revise_brief_then_regenerate or regenerate_from_scratch")
        if not has_text(data.get("strategy_change_reason")):
            errors.append("strategy_change_reason is required when strategy_preserved is false")

    validate_findings(data, errors)
    validate_prompt(data, errors)
    validate_visual(data, errors)

    if decision == "revise_brief_then_regenerate":
        revision_bases = [
            review_path.parent,
            brief_path.parent if brief_path else review_path.parent.parent,
            Path.cwd(),
            repo_root(),
        ]
        revision_path = resolve_existing_path(data.get("brief_revision_path"), revision_bases)
        if not has_text(data.get("brief_revision_path")):
            errors.append("brief_revision_path is required for revise_brief_then_regenerate")
        elif not revision_path:
            errors.append(f"brief_revision_path does not resolve: {data.get('brief_revision_path')} (tried bases: {describe_bases(revision_bases)})")

    context = {
        "brief_path": brief_path,
        "brief": brief,
        "design_path": review_design_path,
        "brief_design_path": brief_design_path,
    }
    return data, context, errors


def main(argv):
    if len(argv) != 2:
        print("usage: validate_result_review.py <result-review.json>", file=sys.stderr)
        return 1

    data, context, errors = validate_review(argv[1])
    if errors:
        print("invalid result review:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"valid: {Path(argv[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
