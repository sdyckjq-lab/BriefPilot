#!/usr/bin/env python3
import json
import sys
from pathlib import Path


WEIGHTS = {
    "audience_clarity": 15,
    "business_goal": 15,
    "content_completeness": 15,
    "brand_context": 15,
    "visual_direction": 10,
    "interaction_scope": 10,
    "asset_availability": 10,
    "constraints": 10,
}


def get(data, *path):
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def list_count(data, *path):
    value = get(data, *path)
    return len(value) if isinstance(value, list) else 0


def has_at_least(data, path, count):
    return list_count(data, *path) >= count


def criterion(label, points, passed):
    return {"label": label, "points": points, "passed": passed}


def score_dimension(checks):
    return sum(check["points"] for check in checks if check["passed"])


def score_dimensions(data):
    checks = {
        "audience_clarity": [
            criterion("primary user", 4, has_value(get(data, "audience", "primary_user"))),
            criterion("context of use", 3, has_value(get(data, "audience", "context_of_use"))),
            criterion("at least two pain points", 4, has_at_least(data, ("audience", "pain_points"), 2)),
            criterion("at least two jobs to be done", 4, has_at_least(data, ("audience", "jobs_to_be_done"), 2)),
        ],
        "business_goal": [
            criterion("business goal", 4, has_value(get(data, "goals", "business_goal"))),
            criterion("design goal", 4, has_value(get(data, "goals", "design_goal"))),
            criterion("conversion goal", 3, has_value(get(data, "goals", "conversion_goal"))),
            criterion("specific CTA", 2, has_value(get(data, "goals", "primary_cta")) or has_value(get(data, "goals", "secondary_cta"))),
            criterion("review criteria", 2, has_at_least(data, ("quality_bar", "review_criteria"), 3)),
        ],
        "content_completeness": [
            criterion("core claim", 3, has_value(get(data, "message", "core_claim"))),
            criterion("supporting points", 3, has_at_least(data, ("message", "supporting_points"), 2)),
            criterion("proof points", 3, has_at_least(data, ("message", "proof_points"), 2)),
            criterion("complete section list", 3, has_at_least(data, ("structure", "sections"), 5)),
            criterion("section-level detail", 3, has_at_least(data, ("structure", "section_details"), 5)),
        ],
        "brand_context": [
            criterion("brand name", 2, has_value(get(data, "brand", "brand_name"))),
            criterion("color direction", 3, has_at_least(data, ("brand", "colors"), 3)),
            criterion("typography direction", 2, has_at_least(data, ("brand", "typography"), 1)),
            criterion("brand voice", 2, has_value(get(data, "brand", "voice"))),
            criterion("DESIGN.md reference", 3, has_value(get(data, "design_system", "design_md_path"))),
            criterion("token summary", 3, has_at_least(data, ("design_system", "token_summary"), 3)),
        ],
        "visual_direction": [
            criterion("selected visual strategy", 2, has_value(get(data, "visual", "strategy_name"))),
            criterion("tone keywords", 2, has_at_least(data, ("visual", "tone_keywords"), 3)),
            criterion("visual references", 2, has_at_least(data, ("visual", "references"), 2)),
            criterion("differentiators", 2, has_at_least(data, ("visual", "differentiators"), 2)),
            criterion("three strategy options", 2, has_at_least(data, ("strategy_options",), 3)),
        ],
        "interaction_scope": [
            criterion("desktop and mobile screens", 2, has_at_least(data, ("structure", "screens"), 2)),
            criterion("visitor flows", 2, has_at_least(data, ("structure", "flows"), 2)),
            criterion("interaction states", 3, has_at_least(data, ("structure", "interaction_states"), 3)),
            criterion("platform", 1, has_value(get(data, "constraints", "platform"))),
            criterion("responsive requirement", 2, get(data, "constraints", "responsive") is True),
        ],
        "asset_availability": [
            criterion("logo state", 2, has_value(get(data, "brand", "logo"))),
            criterion("available assets", 2, has_at_least(data, ("brand", "existing_assets"), 1)),
            criterion("DESIGN.md asset", 2, has_value(get(data, "design_system", "design_md_path"))),
            criterion("design system assumptions", 2, has_at_least(data, ("design_system", "assumptions"), 1)),
            criterion("content warnings", 2, has_at_least(data, ("message", "content_warnings"), 1)),
        ],
        "constraints": [
            criterion("platform constraint", 2, has_value(get(data, "constraints", "platform"))),
            criterion("tech stack constraint", 2, has_at_least(data, ("constraints", "tech_stack"), 1)),
            criterion("accessibility constraints", 3, has_at_least(data, ("constraints", "accessibility"), 2)),
            criterion("deadline or stage constraint", 1, has_value(get(data, "constraints", "deadline"))),
            criterion("must-avoid constraints", 2, has_at_least(data, ("quality_bar", "must_avoid"), 2)),
        ],
    }
    dimensions = {name: score_dimension(items) for name, items in checks.items()}
    gaps = [
        f"{dimension}: {check['label']}"
        for dimension, items in checks.items()
        for check in items
        if not check["passed"]
    ]
    return dimensions, gaps


def level_for(score):
    if score <= 60:
        return "weak"
    if score <= 80:
        return "ready"
    return "strong"


def risks_for(data, gaps):
    risks = []
    if gaps:
        risks.append("Missing brief details may push generators toward generic output.")
    if has_value(get(data, "assumptions")) or has_value(get(data, "design_system", "assumptions")):
        risks.append("Documented assumptions should be confirmed before final production work.")
    if has_value(get(data, "open_questions")):
        risks.append("Open questions remain for launch-specific proof, integrations, or assets.")
    return risks


def recommended_next_step(score):
    if score <= 60:
        return "Ask focused questions before generating design output."
    if score <= 80:
        return "Fill the listed gaps or proceed only with explicit assumptions."
    return "Proceed to prompt export, then review generated output against the checklist."


def main(argv):
    if len(argv) != 2:
        print("usage: score_brief.py <brief.json>", file=sys.stderr)
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

    dimensions, gaps = score_dimensions(data)
    score = sum(dimensions.values())
    print(
        json.dumps(
            {
                "score": score,
                "level": level_for(score),
                "dimensions": dimensions,
                "gaps": gaps,
                "risks": risks_for(data, gaps),
                "recommended_next_step": recommended_next_step(score),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
