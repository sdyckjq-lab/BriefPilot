#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import check_design_md
import export_prompt
import language_checks


REQUIRED_FILES = [
    "input.txt",
    "diagnosis-and-strategies.md",
    "assumptions.md",
    "design-brief.md",
    "design-brief.json",
    "DESIGN.md",
    "review-checklist.md",
    "reviews/design-md-review.md",
    "reviews/design-md-review.json",
    "prompts/claude-design.txt",
    "prompts/huashu-design.txt",
    "prompts/v0.txt",
]

PROMPTS = [
    "prompts/claude-design.txt",
    "prompts/huashu-design.txt",
    "prompts/v0.txt",
]

DEFAULT_CONTENT_LANGUAGE = "zh-CN"
OUTPUT_LANGUAGE_PHRASE = "Use Simplified Chinese for all user-visible UI copy."
OUTPUT_LANGUAGE_CHINESE_PHRASE = "用户可见 UI 文案必须使用简体中文"
DIAGNOSIS_SECTIONS = [
    ("需求评分", "Brief Score"),
    ("主要缺口", "Main Gaps"),
    ("策略选项", "Strategy Options"),
    ("最终选择", "Final Choice"),
]


def has_text(text, needle):
    return needle.lower() in text.lower()


def resolve_path(raw_path, example_dir):
    candidate = Path(str(raw_path)).expanduser()
    candidates = [candidate] if candidate.is_absolute() else [
        example_dir / candidate,
        Path.cwd() / candidate,
    ]
    for entry in candidates:
        if entry.exists():
            return entry
    return None


def load_json(path, findings):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        findings.append(f"invalid JSON text: {path}: {exc}")
    except json.JSONDecodeError as exc:
        findings.append(f"invalid JSON: {path}: {exc}")
    except OSError as exc:
        findings.append(f"cannot read JSON: {path}: {exc}")
    return {}


def load_json_object(path, findings):
    before = len(findings)
    data = load_json(path, findings)
    if len(findings) != before:
        return {}
    if not isinstance(data, dict):
        findings.append(f"invalid JSON object: {path}")
        return {}
    return data


def check_required_files(example_dir, findings):
    for relative in REQUIRED_FILES:
        path = example_dir / relative
        if not path.is_file():
            findings.append(f"missing required file: {relative}")


def check_diagnosis(example_dir, raw_input, strategy_names, findings):
    path = example_dir / "diagnosis-and-strategies.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for primary, legacy in DIAGNOSIS_SECTIONS:
        if not has_text(text, primary) and not has_text(text, legacy):
            findings.append(f"diagnosis missing section: {primary}")
    if raw_input and raw_input not in text:
        findings.append("diagnosis does not include the raw input")
    for name in strategy_names:
        if name not in text:
            findings.append(f"diagnosis missing strategy option: {name}")


def check_content_language(brief, findings):
    meta = brief.get("meta", {}) if isinstance(brief.get("meta"), dict) else {}
    language = meta.get("content_language")
    if language != DEFAULT_CONTENT_LANGUAGE:
        findings.append(f"design-brief.json meta.content_language must be {DEFAULT_CONTENT_LANGUAGE}")
    elif not language_checks.is_chinese_first_brief(brief):
        findings.append("design-brief.json declares zh-CN but brief values are not Chinese-first")


def check_prompts(example_dir, strategy_names, findings):
    required_headers = ["Task", "Output Language", "Visual Strategy", "DESIGN.md Visual System", "Review Criteria"]
    for relative in PROMPTS:
        path = example_dir / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for header in required_headers:
            if f"\n{header}\n" not in f"\n{text}":
                findings.append(f"{relative} missing header: {header}")
        for name in strategy_names:
            if name not in text:
                findings.append(f"{relative} missing strategy option: {name}")
        if OUTPUT_LANGUAGE_PHRASE not in text or OUTPUT_LANGUAGE_CHINESE_PHRASE not in text:
            findings.append(f"{relative} missing Simplified Chinese output-language rule")
        if not language_checks.is_chinese_first_prompt(text):
            findings.append(f"{relative} declares Simplified Chinese but prompt body is not Chinese-first")


def check_prompt_exports_match(example_dir, brief, findings):
    design_path = resolve_path(brief.get("design_system", {}).get("design_md_path"), example_dir)
    design_text = design_path.read_text(encoding="utf-8") if design_path else ""
    for target, relative in {
        "claude-design": "prompts/claude-design.txt",
        "huashu-design": "prompts/huashu-design.txt",
        "v0": "prompts/v0.txt",
    }.items():
        path = example_dir / relative
        if not path.exists():
            continue
        expected = export_prompt.render_prompt(export_prompt.build_sections(brief, design_text, target))
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
                findings.append(f"{relative} does not match export_prompt.py output")


def check_design_review_report(example_dir, brief, findings):
    design_path = resolve_path(brief.get("design_system", {}).get("design_md_path"), example_dir)
    if not design_path:
        return
    report_path = example_dir / "reviews" / "design-md-review.json"
    markdown_path = example_dir / "reviews" / "design-md-review.md"
    if not report_path.exists() or not markdown_path.exists():
        return
    report = load_json_object(report_path, findings)
    expected = check_design_md.build_report(design_path.resolve(), requested_mode="fallback", official_command=None)
    if report != expected:
        findings.append("reviews/design-md-review.json does not match forced fallback checker output")
    if expected.get("blocking"):
        findings.append("DESIGN.md fallback report has blocking findings")
    expected_markdown = check_design_md.render_markdown(expected)
    if markdown_path.read_text(encoding="utf-8") != expected_markdown:
        findings.append("reviews/design-md-review.md does not match design-md-review.json")

    direction = brief.get("design_system", {}).get("reference_direction", {})
    direction_id = direction.get("id") if isinstance(direction, dict) else None
    if direction_id and report.get("reference_direction", {}).get("id") != direction_id:
        findings.append("design review reference direction does not match design-brief.json")


def check_brief_links(example_dir, brief, findings):
    design_path = brief.get("design_system", {}).get("design_md_path")
    if not design_path or not resolve_path(design_path, example_dir):
        findings.append(f"design_system.design_md_path does not resolve: {design_path}")

    markdown_brief = example_dir / "design-brief.md"
    if markdown_brief.exists():
        text = markdown_brief.read_text(encoding="utf-8")
        if "DESIGN.md" not in text:
            findings.append("design-brief.md does not reference DESIGN.md")
        if "策略选项" not in text and "Strategy Options" not in text:
            findings.append("design-brief.md does not include strategy options")


def check_assumptions(example_dir, brief, findings):
    has_assumptions = bool(brief.get("assumptions")) or bool(brief.get("design_system", {}).get("assumptions"))
    if has_assumptions and not (example_dir / "assumptions.md").exists():
        findings.append("assumptions are used but assumptions.md is missing")


def check_interaction_and_accessibility(brief, findings):
    structure = brief.get("structure", {})
    if len(structure.get("interaction_contract", [])) < 4:
        findings.append("design-brief.json must include an interaction_contract with clickable behavior and states")
    if len(structure.get("responsive_accessibility", [])) < 5:
        findings.append("design-brief.json must include responsive_accessibility requirements")


def main(argv):
    if len(argv) != 2:
        print("usage: validate_golden_demo.py <example-dir>", file=sys.stderr)
        return 1

    example_dir = Path(argv[1])
    findings = []
    if not example_dir.is_dir():
        print(f"missing directory: {example_dir}", file=sys.stderr)
        return 1

    check_required_files(example_dir, findings)
    brief = load_json(example_dir / "design-brief.json", findings)
    raw_input = (example_dir / "input.txt").read_text(encoding="utf-8").strip() if (example_dir / "input.txt").exists() else ""
    strategy_options = brief.get("strategy_options", [])
    strategy_names = [item.get("name", "") for item in strategy_options if isinstance(item, dict) and item.get("name")]

    if len(strategy_names) < 3:
        findings.append("design-brief.json must include at least three strategy options")
    selected_strategy = brief.get("visual", {}).get("strategy_name")
    if selected_strategy and selected_strategy not in strategy_names:
        findings.append("selected visual strategy is not present in strategy_options")

    check_content_language(brief, findings)
    check_assumptions(example_dir, brief, findings)
    check_brief_links(example_dir, brief, findings)
    check_interaction_and_accessibility(brief, findings)
    check_diagnosis(example_dir, raw_input, strategy_names, findings)
    check_prompts(example_dir, strategy_names, findings)
    check_prompt_exports_match(example_dir, brief, findings)
    check_design_review_report(example_dir, brief, findings)

    if findings:
        print("invalid golden demo:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"valid: {example_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
