#!/usr/bin/env python3
import sys
from pathlib import Path

import check_design_md as design_report
import export_modification_prompt
import export_prompt
import language_checks
import validate_brief
import validate_design_md
import validate_result_review


BASE_FILES = [
    "input.txt",
    "diagnosis-and-strategies.md",
    "assumptions.md",
    "design-brief.md",
    "design-brief.json",
    "DESIGN.md",
    "review-checklist.md",
    "reviews/design-md-review.md",
    "reviews/design-md-review.json",
    "prompts/huashu-design.txt",
    "prompts/claude-design.txt",
    "prompts/v0.txt",
]

REVIEW_FILES = [
    "generated-results/brief-revision-case.html",
    "reviews/result-review-pasted-summary.md",
    "reviews/result-review-pasted-summary.json",
    "reviews/result-review-brief-revision.md",
    "reviews/result-review-brief-revision.json",
    "reviews/brief-revision.md",
    "prompts/huashu-design-modification.txt",
    "prompts/claude-design-modification.txt",
    "prompts/v0-modification.txt",
    "prompts/revised-generation.txt",
]

DEFAULT_CONTENT_LANGUAGE = "zh-CN"
OUTPUT_LANGUAGE_PHRASE = "Use Simplified Chinese for all user-visible UI copy."
OUTPUT_LANGUAGE_CHINESE_PHRASE = "用户可见 UI 文案必须使用简体中文"


def has_text_value(value):
    return isinstance(value, str) and bool(value.strip())


def check_required(example_dir, findings):
    for relative in BASE_FILES + REVIEW_FILES:
        path = example_dir / relative
        if not path.is_file():
            findings.append(f"missing required file: {relative}")


def check_base_prompt_exports(example_dir, brief, findings):
    design_text = (example_dir / "DESIGN.md").read_text(encoding="utf-8")
    for target in ["huashu-design", "claude-design", "v0"]:
        path = example_dir / "prompts" / f"{target}.txt"
        if not path.exists():
            continue
        expected = export_prompt.render_prompt(export_prompt.build_sections(brief, design_text, target))
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            findings.append(f"prompts/{target}.txt does not match export_prompt.py output")
        if OUTPUT_LANGUAGE_PHRASE not in actual or OUTPUT_LANGUAGE_CHINESE_PHRASE not in actual:
            findings.append(f"prompts/{target}.txt missing Simplified Chinese output-language rule")
        if not language_checks.is_chinese_first_prompt(actual):
            findings.append(f"prompts/{target}.txt declares Simplified Chinese but prompt body is not Chinese-first")


def check_base_brief(example_dir, brief, findings):
    missing = [field for field in validate_brief.REQUIRED_FIELDS if not validate_brief.has_value(validate_brief.value_at(brief, field))]
    for field in missing:
        findings.append(f"design-brief.json missing field: {field}")
    language = validate_brief.value_at(brief, "meta.content_language")
    if language != DEFAULT_CONTENT_LANGUAGE:
        findings.append(f"design-brief.json meta.content_language must be {DEFAULT_CONTENT_LANGUAGE}")
    elif not language_checks.is_chinese_first_brief(brief):
        findings.append("design-brief.json declares zh-CN but brief values are not Chinese-first")
    if not validate_brief.has_value(brief.get("assumptions")) and not validate_brief.has_value(brief.get("open_questions")):
        findings.append("design-brief.json missing assumptions or open_questions")
    design_path = validate_brief.value_at(brief, "design_system.design_md_path")
    if not validate_brief.resolve_existing_path(design_path, example_dir / "design-brief.json"):
        findings.append(f"design_system.design_md_path does not resolve: {design_path}")


def check_design_md(example_dir, findings):
    path = example_dir / "DESIGN.md"
    text = path.read_text(encoding="utf-8")
    front_matter, body = validate_design_md.split_front_matter(text)
    if front_matter is None:
        findings.append("DESIGN.md missing YAML front matter")
    elif not validate_design_md.front_matter_has_color_entry(front_matter):
        findings.append("DESIGN.md missing colors entry")
    for heading in validate_design_md.REQUIRED_HEADINGS:
        if heading not in body:
            findings.append(f"DESIGN.md missing heading: {heading}")


def check_design_review_report(example_dir, brief, findings):
    report_path = example_dir / "reviews" / "design-md-review.json"
    markdown_path = example_dir / "reviews" / "design-md-review.md"
    if not report_path.exists() or not markdown_path.exists():
        return
    report = validate_result_review.load_json_object(report_path, findings, "reviews/design-md-review.json")
    expected = design_report.build_report((example_dir / "DESIGN.md").resolve(), requested_mode="fallback", official_command=None)
    if report != expected:
        findings.append("reviews/design-md-review.json does not match forced fallback checker output")
    if expected.get("blocking"):
        findings.append("DESIGN.md fallback report has blocking findings")
    expected_markdown = design_report.render_markdown(expected)
    if markdown_path.read_text(encoding="utf-8") != expected_markdown:
        findings.append("reviews/design-md-review.md does not match design-md-review.json")
    direction = brief.get("design_system", {}).get("reference_direction", {})
    direction_id = direction.get("id") if isinstance(direction, dict) else None
    if direction_id and report.get("reference_direction", {}).get("id") != direction_id:
        findings.append("design review reference direction does not match design-brief.json")


def check_review(review_path, findings):
    review, context, errors = validate_result_review.validate_review(review_path)
    findings.extend(errors)
    return review, context


def check_review_markdown(markdown_path, review, findings):
    text = markdown_path.read_text(encoding="utf-8")
    text_lower = text.lower()
    relative = markdown_path.relative_to(markdown_path.parents[1])
    evidence = review.get("evidence") if isinstance(review.get("evidence"), dict) else {}

    expected_values = [
        ("decision", review.get("decision")),
        ("selected strategy", review.get("selected_strategy")),
        ("evidence kind", evidence.get("kind")),
        ("prompt intent", review.get("prompt_intent")),
        ("brief revision", review.get("brief_revision_path")),
    ]
    for label, value in expected_values:
        if has_text_value(value) and value.lower() not in text_lower:
            findings.append(f"{relative} markdown {label} does not match JSON: {value}")

    for index, finding in enumerate(review.get("findings", [])):
        if not isinstance(finding, dict):
            continue
        for field in ["issue", "recommended_change"]:
            value = finding.get(field)
            if has_text_value(value) and value.lower() not in text_lower:
                findings.append(f"{relative} markdown finding[{index}].{field} does not match JSON")


def check_modification_prompt(review_path, target, prompt_path, findings):
    review, context, errors = validate_result_review.validate_review(review_path)
    if errors:
        findings.extend(errors)
        return
    design_text = context["design_path"].read_text(encoding="utf-8")
    brief_revision_text = ""
    if review.get("brief_revision_path"):
        revision_path = validate_result_review.resolve_existing_path(
            review.get("brief_revision_path"),
            [review_path.parent, context["brief_path"].parent, Path.cwd(), validate_result_review.repo_root()],
        )
        if revision_path:
            brief_revision_text = revision_path.read_text(encoding="utf-8")
    expected = export_modification_prompt.build_prompt(review, context, target, design_text, brief_revision_text)
    if prompt_path.read_text(encoding="utf-8") != expected:
        findings.append(f"{prompt_path.relative_to(review_path.parents[1])} does not match export_modification_prompt.py output")
    prompt_text = prompt_path.read_text(encoding="utf-8")
    if "DESIGN.md Visual Rules To Preserve" not in prompt_text:
        findings.append(f"{prompt_path.relative_to(review_path.parents[1])} is missing DESIGN.md visual guidance")
    if OUTPUT_LANGUAGE_PHRASE not in prompt_text or OUTPUT_LANGUAGE_CHINESE_PHRASE not in prompt_text:
        findings.append(f"{prompt_path.relative_to(review_path.parents[1])} missing Simplified Chinese output-language rule")
    if not language_checks.is_chinese_first_prompt(prompt_text):
        findings.append(f"{prompt_path.relative_to(review_path.parents[1])} declares Simplified Chinese but prompt body is not Chinese-first")


def check_workspace_content(example_dir, findings):
    brief_text = (example_dir / "design-brief.md").read_text(encoding="utf-8")
    brief_json_text = (example_dir / "design-brief.json").read_text(encoding="utf-8")
    required = [
        "研究工作台",
        "来源详情",
        "低可信度",
        "权限受限",
        "保存/分享",
        "移动端",
    ]
    for phrase in required:
        if phrase.lower() not in (brief_text + "\n" + brief_json_text).lower():
            findings.append(f"workspace brief missing phrase: {phrase}")
    if "landing page" in brief_json_text.lower():
        findings.append("workspace brief must not be described as a landing-page example")


def main(argv):
    if len(argv) != 2:
        print("usage: validate_review_demo.py <example-dir>", file=sys.stderr)
        return 1

    example_dir = Path(argv[1])
    findings = []
    if not example_dir.is_dir():
        print(f"missing directory: {example_dir}", file=sys.stderr)
        return 1

    check_required(example_dir, findings)
    if findings:
        print("invalid review demo:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    brief = validate_result_review.load_json_object(example_dir / "design-brief.json", findings, "design-brief.json")
    check_base_brief(example_dir, brief, findings)
    check_design_md(example_dir, findings)
    check_design_review_report(example_dir, brief, findings)
    check_base_prompt_exports(example_dir, brief, findings)
    check_workspace_content(example_dir, findings)

    pasted_review_path = example_dir / "reviews" / "result-review-pasted-summary.json"
    revision_review_path = example_dir / "reviews" / "result-review-brief-revision.json"
    pasted_review, _ = check_review(pasted_review_path, findings)
    revision_review, _ = check_review(revision_review_path, findings)
    check_review_markdown(example_dir / "reviews" / "result-review-pasted-summary.md", pasted_review, findings)
    check_review_markdown(example_dir / "reviews" / "result-review-brief-revision.md", revision_review, findings)

    if pasted_review.get("evidence", {}).get("kind") != "pasted_summary":
        findings.append("pasted summary review must use evidence.kind pasted_summary")
    if pasted_review.get("evidence", {}).get("path"):
        findings.append("pasted summary review must not require evidence.path")
    if revision_review.get("evidence", {}).get("kind") != "local_file":
        findings.append("brief-revision review must use evidence.kind local_file")

    for target in ["huashu-design", "claude-design", "v0"]:
        check_modification_prompt(
            pasted_review_path,
            target,
            example_dir / "prompts" / f"{target}-modification.txt",
            findings,
        )
    check_modification_prompt(
        revision_review_path,
        "generic",
        example_dir / "prompts" / "revised-generation.txt",
        findings,
    )

    if findings:
        print("invalid review demo:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"valid: {example_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
