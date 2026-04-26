#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import validate_result_review


TARGETS = {"huashu-design", "claude-design", "v0", "generic"}


def portable_path(path):
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(validate_result_review.repo_root()))
    except ValueError:
        return str(resolved)


def join_list(values):
    if not values:
        return "- None"
    return "\n".join(f"- {value}" for value in values if str(value).strip())


def format_findings(findings):
    lines = []
    for item in findings:
        lines.append(
            "- {severity}: {issue} | Reference: {brief_reference} | Evidence: {evidence} | Change: {recommended_change}".format(
                severity=item.get("severity", ""),
                issue=item.get("issue", ""),
                brief_reference=item.get("brief_reference", ""),
                evidence=item.get("evidence", ""),
                recommended_change=item.get("recommended_change", ""),
            )
        )
    return "\n".join(lines) if lines else "- None"


def compact(parts):
    return "\n".join(str(part).strip() for part in parts if str(part).strip())


def value_at(data, dotted_path):
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def format_inline(value):
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, dict):
        return ", ".join(f"{key}: {format_inline(item)}" for key, item in value.items() if format_inline(item))
    if value is None:
        return ""
    return str(value).strip()


def format_named_items(value):
    if not isinstance(value, list) or not value:
        return "- None"
    lines = []
    for item in value:
        if isinstance(item, dict):
            name = item.get("name") or item.get("title") or item.get("label") or "Item"
            detail = ", ".join(
                f"{key}: {format_inline(entry)}"
                for key, entry in item.items()
                if key not in {"name", "title", "label"} and format_inline(entry)
            )
            lines.append(f"- {name}: {detail}" if detail else f"- {name}")
        elif str(item).strip():
            lines.append(f"- {item}")
    return "\n".join(lines) if lines else "- None"


def format_brief_context(brief):
    if not isinstance(brief, dict) or not brief:
        return "- Brief content unavailable"

    summary_lines = [
        f"Project: {format_inline(value_at(brief, 'project.name'))}",
        f"Task type: {format_inline(value_at(brief, 'project.task_type'))}",
        f"Summary: {format_inline(value_at(brief, 'project.summary'))}",
        f"Primary user: {format_inline(value_at(brief, 'audience.primary_user'))}",
        f"Business goal: {format_inline(value_at(brief, 'goals.business_goal'))}",
        f"Design goal: {format_inline(value_at(brief, 'goals.design_goal'))}",
        f"Core claim: {format_inline(value_at(brief, 'message.core_claim'))}",
        f"Selected strategy: {format_inline(validate_result_review.selected_strategy(brief))}",
    ]
    structure_lines = [
        f"Sections: {format_inline(value_at(brief, 'structure.sections'))}",
        f"Section details:\n{format_named_items(value_at(brief, 'structure.section_details'))}",
        f"Interaction contract: {format_inline(value_at(brief, 'structure.interaction_contract'))}",
        f"Responsive/accessibility: {format_inline(value_at(brief, 'structure.responsive_accessibility'))}",
    ]
    quality_lines = [
        f"Must have: {format_inline(value_at(brief, 'quality_bar.must_have'))}",
        f"Review Criteria: {format_inline(value_at(brief, 'quality_bar.review_criteria'))}",
        f"Must avoid: {format_inline(value_at(brief, 'quality_bar.must_avoid'))}",
    ]

    return compact(
        [
            "Brief Summary",
            "\n".join(line for line in summary_lines if line.split(": ", 1)[-1]),
            "Required Structure And States",
            "\n".join(line for line in structure_lines if line.split(": ", 1)[-1] and not line.endswith("- None")),
            "Quality Bar",
            "\n".join(line for line in quality_lines if line.split(": ", 1)[-1]),
            "Full Brief JSON",
            "```json\n" + json.dumps(brief, ensure_ascii=False, indent=2) + "\n```",
        ]
    )


def read_template():
    return (Path(__file__).resolve().parents[1] / "templates" / "modification-prompt.txt").read_text(encoding="utf-8")


def render(template, mapping):
    text = template
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def resolve_override(raw_path, expected_path, field_name, bases):
    if not raw_path:
        return expected_path, []
    candidate = Path(raw_path).expanduser()
    candidates = [candidate] if candidate.is_absolute() else [base / candidate for base in bases]
    candidate = next((entry.resolve() for entry in candidates if entry.is_file()), None)
    if not candidate:
        return None, [f"{field_name} does not resolve: {raw_path}"]
    if candidate != expected_path:
        return candidate, [f"{field_name} must resolve to the same file as the review and brief package"]
    return candidate, []


def build_prompt(review, context, target, design_text, brief_revision_text=""):
    decision = review["decision"]
    if decision == "accept":
        raise ValueError("decision accept does not need a modification prompt")

    if decision == "tweak":
        task = "Apply a targeted modification to the generated result. Preserve the approved strategy and visual system."
    elif decision == "revise_brief_then_regenerate":
        task = "Regenerate the result after applying the brief revision guidance below. Preserve the approved strategy unless the review explicitly changes it."
    else:
        task = "Regenerate the result from scratch using the saved brief package and the review findings below."

    strategy_preservation = "Preserve the selected strategy."
    if not review.get("strategy_preserved"):
        strategy_preservation = f"Strategy may change only for this reason: {review.get('strategy_change_reason', '')}"

    evidence = review.get("evidence", {})
    visual = review.get("visual_review", {})
    prompt = review.get("prompt", {})
    review_summary = compact(
        [
            f"Evidence kind: {evidence.get('kind', '')}",
            f"Evidence summary: {evidence.get('summary', '')}",
            f"Visual review status: {visual.get('status', '')}",
            f"Visual review notes: {visual.get('notes', '')}",
        ]
    )

    mapping = {
        "task": task,
        "target_tool": target,
        "decision": decision,
        "selected_strategy": review.get("selected_strategy", ""),
        "strategy_preservation": strategy_preservation,
        "brief_path": portable_path(context["brief_path"]),
        "design_md_path": portable_path(context["design_path"]),
        "brief_context": format_brief_context(context.get("brief")),
        "design_md": design_text.strip(),
        "review_summary": review_summary,
        "keep": join_list(prompt.get("keep", [])),
        "change": join_list(prompt.get("change", [])),
        "do_not_change": join_list(prompt.get("do_not_change", [])),
        "findings": format_findings(review.get("findings", [])),
        "brief_revision": brief_revision_text.strip() or "- None",
        "acceptance_checks": join_list(prompt.get("acceptance_checks", [])),
    }
    rendered = render(read_template(), mapping).rstrip() + "\n"
    if "DESIGN.md Visual Rules To Preserve" not in rendered or not design_text.strip():
        raise ValueError("exported prompt would omit DESIGN.md visual guidance")
    if "Source Brief Context" not in rendered or "Full Brief JSON" not in rendered:
        raise ValueError("exported prompt would omit source brief content")
    return rendered


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", required=True)
    parser.add_argument("--brief")
    parser.add_argument("--design")
    parser.add_argument("--target", choices=sorted(TARGETS))
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    review, context, errors = validate_result_review.validate_review(args.review)
    if errors:
        print("invalid result review:")
        for error in errors:
            print(f"- {error}")
        return 1

    target = args.target or review.get("target_tool")
    if target not in TARGETS:
        print(f"invalid target: {target}", file=sys.stderr)
        return 1

    brief_path, override_errors = resolve_override(
        args.brief,
        context["brief_path"],
        "--brief",
        [Path.cwd(), context["brief_path"].parent, validate_result_review.repo_root()],
    )
    errors.extend(override_errors)
    design_path, override_errors = resolve_override(
        args.design,
        context["design_path"],
        "--design",
        [Path.cwd(), context["design_path"].parent, context["brief_path"].parent, validate_result_review.repo_root()],
    )
    errors.extend(override_errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    try:
        design_text = design_path.read_text(encoding="utf-8")
        brief_revision_text = ""
        if review.get("brief_revision_path"):
            review_path = Path(args.review)
            revision_path = validate_result_review.resolve_existing_path(
                review.get("brief_revision_path"),
                [review_path.parent, brief_path.parent, Path.cwd(), validate_result_review.repo_root()],
            )
            if revision_path:
                brief_revision_text = revision_path.read_text(encoding="utf-8")
        rendered = build_prompt(review, {**context, "brief_path": brief_path, "design_path": design_path}, target, design_text, brief_revision_text)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
