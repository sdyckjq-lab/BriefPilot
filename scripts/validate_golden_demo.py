#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import check_design_md
import export_modification_prompt
import export_prompt
import language_checks
import validate_result_review
import validate_user_flow_package


REQUIRED_FILES = [
    "input.txt",
    "START_HERE.md",
    "demo-evidence.md",
    "diagnosis-and-strategies.md",
    "assumptions.md",
    "design-spec.md",
    "design-brief.md",
    "design-brief.json",
    "DESIGN.md",
    "review-checklist.md",
    "first-pass/controlled-baseline.md",
    "second-pass/briefpilot-reviewed.md",
    "reviews/design-md-review.md",
    "reviews/design-md-review.json",
    "reviews/result-review-first-pass.md",
    "reviews/result-review-first-pass.json",
    "prompts/generic-modification.txt",
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
PRIVATE_TEXT = [
    "/" + "Users/",
    "Desktop/" + "project",
    "kang" + "jiaqi",
]
DEMO_EVIDENCE_SECTIONS = [
    "原始输入",
    "运行信息",
    "完整作品规范",
    "第一版结果",
    "BriefPilot Review",
    "第二版结果",
    "公开说明",
]
DEMO_EVIDENCE_PATHS = [
    "design-spec.md",
    "first-pass/controlled-baseline.md",
    "reviews/result-review-first-pass.md",
    "reviews/result-review-first-pass.json",
    "prompts/generic-modification.txt",
    "second-pass/briefpilot-reviewed.md",
]
FIRST_PASS_PATH = "first-pass/controlled-baseline.md"
SECOND_PASS_PATH = "second-pass/briefpilot-reviewed.md"
REVIEW_MODIFICATION_PROMPT_PATH = "prompts/generic-modification.txt"
FIRST_PASS_REQUIRED_PHRASES = [
    "受控基线",
    "不是命名工具输出",
    "帮我做一个 AI 搜索产品官网",
    "带来源答案",
    "加载状态",
    "企业信任型",
]
SECOND_PASS_REQUIRED_PHRASES = [
    "同一份 `design-spec.md`",
    "`DESIGN.md`",
    "第一版评审",
    "企业信任型",
    "加载",
    "低可信度",
    "验收标准",
]
MODIFICATION_PROMPT_REQUIRED_PHRASES = [
    "Apply a targeted modification",
    "企业信任型",
    "让首屏明确表达带来源的 AI 搜索",
    "加入带来源答案、引用标签和可信度标记的产品界面",
    "补齐加载、错误、空状态、低可信度、移动端和键盘焦点要求",
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


def normalized_relative_path(raw_path):
    if not raw_path:
        return ""
    return Path(str(raw_path)).as_posix().removeprefix("./")


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


def read_text_file(path, findings, relative):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        findings.append(f"{relative} is not readable UTF-8: {exc}")
    except OSError as exc:
        findings.append(f"{relative} cannot be read: {exc}")
    return ""


def check_no_private_text(example_dir, findings):
    for path in sorted(example_dir.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".txt", ".json", ".html"}:
            continue
        relative = path.relative_to(example_dir).as_posix()
        text = read_text_file(path, findings, relative)
        for token in PRIVATE_TEXT:
            if token in text:
                findings.append(f"{relative} contains forbidden local text: {token}")


def check_demo_evidence(example_dir, raw_input, findings):
    path = example_dir / "demo-evidence.md"
    if not path.exists():
        return
    text = read_text_file(path, findings, "demo-evidence.md")
    if not text:
        return
    for section in DEMO_EVIDENCE_SECTIONS:
        if f"## {section}" not in text:
            findings.append(f"demo-evidence.md missing section: {section}")
    if raw_input and raw_input not in text:
        findings.append("demo-evidence.md does not include the raw input")
    for phrase in ["受控基线", "不是命名工具输出", "是否人工修改", "可复现"]:
        if phrase not in text:
            findings.append(f"demo-evidence.md missing evidence disclosure: {phrase}")
    for relative in DEMO_EVIDENCE_PATHS:
        if relative not in text:
            findings.append(f"demo-evidence.md missing evidence path: {relative}")
        elif not (example_dir / relative).is_file():
            findings.append(f"demo-evidence.md points to missing file: {relative}")


def check_demo_result_files(example_dir, findings):
    required_by_file = {
        FIRST_PASS_PATH: FIRST_PASS_REQUIRED_PHRASES,
        SECOND_PASS_PATH: SECOND_PASS_REQUIRED_PHRASES,
    }
    for relative, phrases in required_by_file.items():
        path = example_dir / relative
        if not path.exists():
            continue
        text = read_text_file(path, findings, relative)
        for phrase in phrases:
            if phrase not in text:
                findings.append(f"{relative} missing evidence detail: {phrase}")


def external_prompt_source(review):
    next_actions = review.get("next_actions") if isinstance(review.get("next_actions"), dict) else {}
    source = next_actions.get("next_copy_source")
    options = next_actions.get("options")
    option_source = ""
    if isinstance(options, list):
        for option in options:
            if isinstance(option, dict) and option.get("action") == "external_prompt":
                option_source = option.get("next_copy_source")
                break
    return next_actions, source, option_source


def check_first_pass_modification_prompt(example_dir, review, context, findings):
    next_actions, source, option_source = external_prompt_source(review)
    if next_actions.get("recommended_next_action") != "external_prompt":
        findings.append("reviews/result-review-first-pass.json must recommend external_prompt")

    if normalized_relative_path(source) != REVIEW_MODIFICATION_PROMPT_PATH:
        findings.append(f"reviews/result-review-first-pass.json next_copy_source must be {REVIEW_MODIFICATION_PROMPT_PATH}")
    if normalized_relative_path(option_source) != REVIEW_MODIFICATION_PROMPT_PATH:
        findings.append(f"reviews/result-review-first-pass.json external_prompt option next_copy_source must be {REVIEW_MODIFICATION_PROMPT_PATH}")
    if normalized_relative_path(source) in PROMPTS:
        findings.append("reviews/result-review-first-pass.json next_copy_source points to a first-generation prompt")

    prompt_path = resolve_path(source, example_dir)
    if not prompt_path:
        findings.append(f"reviews/result-review-first-pass.json next_copy_source does not resolve: {source}")
        return

    relative = prompt_path.relative_to(example_dir).as_posix() if prompt_path.is_relative_to(example_dir) else str(prompt_path)
    prompt_text = read_text_file(prompt_path, findings, relative)
    for phrase in MODIFICATION_PROMPT_REQUIRED_PHRASES:
        if phrase not in prompt_text:
            findings.append(f"{relative} missing modification prompt detail: {phrase}")

    try:
        in_source_tree = example_dir.resolve().is_relative_to(validate_result_review.repo_root())
    except OSError:
        in_source_tree = False
    if not in_source_tree:
        return

    design_path = context.get("design_path")
    if not design_path:
        return
    try:
        design_text = design_path.read_text(encoding="utf-8")
        expected = export_modification_prompt.build_prompt(
            review,
            context,
            review.get("target_tool"),
            design_text,
            "",
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        findings.append(f"{relative} cannot be validated against export_modification_prompt.py: {exc}")
        return
    if prompt_text != expected:
        findings.append(f"{relative} does not match export_modification_prompt.py output")


def check_first_pass_result_review(example_dir, findings):
    review_path = example_dir / "reviews" / "result-review-first-pass.json"
    review = {}
    context = {}
    errors = []
    if review_path.exists():
        review, context, errors = validate_result_review.validate_review(review_path)
        for error in errors:
            findings.append(f"reviews/result-review-first-pass.json invalid: {error}")
        if not errors:
            evidence = review.get("evidence") if isinstance(review.get("evidence"), dict) else {}
            if evidence.get("kind") != "local_file":
                findings.append("reviews/result-review-first-pass.json evidence.kind must be local_file")
            expected_evidence = (example_dir / FIRST_PASS_PATH).resolve()
            resolved_evidence = resolve_path(evidence.get("path"), example_dir)
            if not resolved_evidence or resolved_evidence.resolve() != expected_evidence:
                findings.append(f"reviews/result-review-first-pass.json evidence.path must resolve to {FIRST_PASS_PATH}")
            if normalized_relative_path(evidence.get("path")) != FIRST_PASS_PATH:
                findings.append(f"reviews/result-review-first-pass.json evidence.path must be {FIRST_PASS_PATH}")
            check_first_pass_modification_prompt(example_dir, review, context, findings)

    markdown_path = example_dir / "reviews" / "result-review-first-pass.md"
    if markdown_path.exists():
        text = read_text_file(markdown_path, findings, "reviews/result-review-first-pass.md")
        for phrase in ["Decision: `tweak`", "second-pass/briefpilot-reviewed.md", "prompts/generic-modification.txt", "企业信任型"]:
            if phrase not in text:
                findings.append(f"reviews/result-review-first-pass.md missing evidence detail: {phrase}")


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
    findings.extend(validate_user_flow_package.validate_package(example_dir))
    check_assumptions(example_dir, brief, findings)
    check_brief_links(example_dir, brief, findings)
    check_interaction_and_accessibility(brief, findings)
    check_diagnosis(example_dir, raw_input, strategy_names, findings)
    check_prompts(example_dir, strategy_names, findings)
    check_prompt_exports_match(example_dir, brief, findings)
    check_design_review_report(example_dir, brief, findings)
    check_demo_evidence(example_dir, raw_input, findings)
    check_demo_result_files(example_dir, findings)
    check_first_pass_result_review(example_dir, findings)
    check_no_private_text(example_dir, findings)

    if findings:
        print("invalid golden demo:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"valid: {example_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
