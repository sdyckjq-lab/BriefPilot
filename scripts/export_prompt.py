#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


TARGET_DELIVERABLES = {
    "huashu-design": "Create a high-fidelity HTML prototype with real product surfaces, clickable interactions, and reviewable visual detail.",
    "claude-design": "Create a visual artifact with clear variants and leave room for iterative visual tweaks.",
    "v0": "Create a runnable React or Next.js UI component, using shadcn/ui and Tailwind-compatible tokens when suitable.",
}

SUPPORTED_CONTENT_LANGUAGES = {"zh-CN"}
DEFAULT_CONTENT_LANGUAGE = "zh-CN"
OUTPUT_LANGUAGE_RULES = {
    "zh-CN": "\n".join(
        [
            "用户可见 UI 文案必须使用简体中文（Simplified Chinese / zh-CN）。",
            "Use Simplified Chinese for all user-visible UI copy.",
            "代码标识、文件名、组件名、命令示例、design token keys 和工具名保持英文。",
            "如果输入里有用户原话引用，除非明确要求翻译，否则保持原文。",
        ]
    )
}


SECTION_ORDER = [
    "Task",
    "Context",
    "Audience",
    "Goal",
    "Output Language",
    "Visual Strategy",
    "DESIGN.md Visual System",
    "Required Content",
    "Constraints",
    "Do Not Do",
    "Deliverable",
    "Review Criteria",
]


def join_list(values):
    if not values:
        return ""
    return "\n".join(f"- {value}" for value in values)


def join_named_items(values, fields):
    if not values:
        return ""
    lines = []
    for item in values:
        if not isinstance(item, dict):
            lines.append(f"- {item}")
            continue
        name = item.get("name") or item.get("section") or "Item"
        suffix = " (selected)" if item.get("selected") else ""
        details = []
        for label, key in fields:
            value = item.get(key)
            if isinstance(value, list):
                value = ", ".join(str(entry) for entry in value if str(entry).strip())
            if value:
                details.append(f"{label}: {value}")
        lines.append(f"- {name}{suffix}: {'; '.join(details)}")
    return "\n".join(lines)


def compact(parts):
    return "\n".join(str(part).strip() for part in parts if str(part).strip())


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_optional(path):
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def content_language(brief):
    meta = brief.get("meta", {}) if isinstance(brief.get("meta", {}), dict) else {}
    language = meta.get("content_language") or DEFAULT_CONTENT_LANGUAGE
    if language not in SUPPORTED_CONTENT_LANGUAGES:
        return DEFAULT_CONTENT_LANGUAGE
    return language


def build_sections(brief, design_text, target):
    project = brief.get("project", {})
    audience = brief.get("audience", {})
    goals = brief.get("goals", {})
    message = brief.get("message", {})
    structure = brief.get("structure", {})
    visual = brief.get("visual", {})
    design_system = brief.get("design_system", {})
    constraints = brief.get("constraints", {})
    quality_bar = brief.get("quality_bar", {})
    strategy_options = brief.get("strategy_options", [])

    task = compact(
        [
            f"Create {project.get('name') or 'the requested design'}.",
            f"Task type: {project.get('task_type', '')}.",
        ]
    )
    context = compact(
        [
            project.get("summary", ""),
            f"Stage: {project.get('stage', '')}" if project.get("stage") else "",
            "Pain points:",
            join_list(audience.get("pain_points", [])),
            "Jobs to be done:",
            join_list(audience.get("jobs_to_be_done", [])),
        ]
    )
    audience_text = compact(
        [
            f"Primary: {audience.get('primary_user', '')}",
            f"Secondary: {audience.get('secondary_user', '')}",
            f"Context: {audience.get('context_of_use', '')}",
        ]
    )
    goal = compact(
        [
            f"Business goal: {goals.get('business_goal', '')}",
            f"Design goal: {goals.get('design_goal', '')}",
            f"Conversion goal: {goals.get('conversion_goal', '')}",
            f"Primary CTA: {goals.get('primary_cta', '')}",
            f"Secondary CTA: {goals.get('secondary_cta', '')}",
        ]
    )
    output_language = OUTPUT_LANGUAGE_RULES[content_language(brief)]
    visual_strategy = compact(
        [
            f"Strategy: {visual.get('strategy_name', '')}",
            "Strategy options:",
            join_named_items(
                strategy_options,
                [
                    ("best use", "best_use_case"),
                    ("tone", "visual_tone"),
                    ("structure", "information_structure_focus"),
                    ("risk", "risk"),
                    ("tools", "best_target_tools"),
                ],
            ),
            "Tone keywords:",
            join_list(visual.get("tone_keywords", [])),
            "References:",
            join_list(visual.get("references", [])),
            "Differentiators:",
            join_list(visual.get("differentiators", [])),
        ]
    )
    design_md = design_text.strip() or compact(
        [
            f"DESIGN.md path: {design_system.get('design_md_path', '')}",
            "Token summary:",
            join_list(design_system.get("token_summary", [])),
            "Design system assumptions:",
            join_list(design_system.get("assumptions", [])),
        ]
    )
    required_content = compact(
        [
            f"Core claim: {message.get('core_claim', '')}",
            "Supporting points:",
            join_list(message.get("supporting_points", [])),
            "Proof points:",
            join_list(message.get("proof_points", [])),
            "Sections:",
            join_list(structure.get("sections", [])),
            "Section details:",
            join_named_items(
                structure.get("section_details", []),
                [
                    ("purpose", "purpose"),
                    ("content", "content"),
                    ("visual anchor", "visual_anchor"),
                ],
            ),
            "Screens:",
            join_list(structure.get("screens", [])),
            "Flows:",
            join_list(structure.get("flows", [])),
            "Interaction states:",
            join_list(structure.get("interaction_states", [])),
            "Interaction contract:",
            join_list(structure.get("interaction_contract", [])),
        ]
    )
    constraints_text = compact(
        [
            f"Platform: {constraints.get('platform', '')}",
            f"Responsive: {constraints.get('responsive', '')}",
            "Tech stack:",
            join_list(constraints.get("tech_stack", [])),
            "Accessibility:",
            join_list(constraints.get("accessibility", [])),
            "Responsive and accessibility requirements:",
            join_list(structure.get("responsive_accessibility", [])),
            f"Deadline: {constraints.get('deadline', '')}",
        ]
    )
    avoid = compact(
        [
            "Forbidden visual directions:",
            join_list(visual.get("avoid", [])),
            "Must avoid:",
            join_list(quality_bar.get("must_avoid", [])),
            "Content warnings:",
            join_list(message.get("content_warnings", [])),
        ]
    )
    deliverable = TARGET_DELIVERABLES[target]
    review = compact(
        [
            "Must have:",
            join_list(quality_bar.get("must_have", [])),
            "Review criteria:",
            join_list(quality_bar.get("review_criteria", [])),
        ]
    )

    return {
        "Task": task,
        "Context": context,
        "Audience": audience_text,
        "Goal": goal,
        "Output Language": output_language,
        "Visual Strategy": visual_strategy,
        "DESIGN.md Visual System": design_md,
        "Required Content": required_content,
        "Constraints": constraints_text,
        "Do Not Do": avoid,
        "Deliverable": deliverable,
        "Review Criteria": review,
    }


def render_prompt(sections):
    rendered = []
    for heading in SECTION_ORDER:
        rendered.append(heading)
        rendered.append(sections.get(heading, "").strip())
        rendered.append("")
    return "\n".join(rendered).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True)
    parser.add_argument("--design")
    parser.add_argument("--target", required=True, choices=sorted(TARGET_DELIVERABLES))
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    try:
        brief = load_json(args.brief)
        design_text = read_optional(args.design)
    except FileNotFoundError as exc:
        print(f"missing file: {exc.filename}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid json: {exc}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_prompt(build_sections(brief, design_text, args.target)), encoding="utf-8")
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
