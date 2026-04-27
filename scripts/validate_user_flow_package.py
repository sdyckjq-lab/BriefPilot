#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import export_design_spec
import language_checks


DEFAULT_CONTENT_LANGUAGE = "zh-CN"
PRIVATE_TEXT = [
    "/" + "Users/",
    "Desktop/" + "project",
    "kang" + "jiaqi",
]
SOURCE_MATERIAL_TEXT = [
    "BriefPilot_" + "需求文档.md",
    "ClaudeDesign_" + "泄露" + "提示词.md",
    "Google_" + "DESIGN.md_" + "README.md",
    "Google_" + "DESIGN.md_" + "完整规范.md",
    "泄露" + "提示词",
]


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def load_json_object(path, findings, label):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        findings.append(f"missing {label}: {path.name}")
        return {}
    except UnicodeDecodeError as error:
        findings.append(f"{label} is not readable UTF-8: {error}")
        return {}
    except json.JSONDecodeError as error:
        findings.append(f"{label} invalid json: {error}")
        return {}
    if not isinstance(data, dict):
        findings.append(f"{label} must be a JSON object")
        return {}
    return data


def value_at(data, dotted_path, default=""):
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current if current is not None else default


def read_text(path, findings, label):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        findings.append(f"missing required user-flow file: {label}")
    except UnicodeDecodeError as error:
        findings.append(f"{label} is not readable UTF-8: {error}")
    except OSError as error:
        findings.append(f"{label} cannot be read: {error}")
    return ""


def resolve_existing_file(raw_path, bases):
    if not has_text(raw_path):
        return None
    candidate = Path(raw_path).expanduser()
    candidates = [candidate] if candidate.is_absolute() else [base / candidate for base in bases]
    for entry in candidates:
        if entry.is_file():
            return entry.resolve()
    return None


def check_no_private_text(relative, text, findings):
    for token in PRIVATE_TEXT:
        if token in text:
            findings.append(f"{relative} contains forbidden local text: {token}")
    for token in SOURCE_MATERIAL_TEXT:
        if token in text:
            findings.append(f"{relative} contains private source material marker")


def check_start_here(text, findings):
    if "design-spec.md" not in text:
        findings.append("START_HERE.md must name design-spec.md as the core copy source")
    for phrase in ["复制整个", "评审", "带回来", "可选导出"]:
        if phrase not in text:
            findings.append(f"START_HERE.md missing required guidance phrase: {phrase}")
    primary_action_lines = [line for line in text.splitlines() if line.strip().startswith("首选下一步：")]
    if len(primary_action_lines) != 1:
        findings.append("START_HERE.md must expose exactly one primary next action")
    if "generic" in text.lower():
        findings.append("START_HERE.md must not expose generic as a first-run prompt target")
    mandatory_prompt_phrases = ["必须选择提示词", "必须使用 prompts/", "三个提示词都要复制", "三份提示词都要复制"]
    for phrase in mandatory_prompt_phrases:
        if phrase in text:
            findings.append("START_HERE.md must not make platform prompts mandatory")


def check_design_spec(package_dir, text, brief, findings):
    expected_strings = [
        value_at(brief, "project.name"),
        value_at(brief, "audience.primary_user"),
        value_at(brief, "goals.design_goal"),
        value_at(brief, "message.core_claim"),
        export_design_spec.selected_strategy(brief),
        "主要任务",
        "首屏",
        "内容清单",
        "交互状态",
        "响应式",
        "可访问性",
        "禁止的通用化结果",
        "不要做泛泛功能卡片",
        "不要虚构客户评价",
        "不要使用模糊 CTA",
        "不要套用通用 dashboard card",
    ]
    for phrase in expected_strings:
        if has_text(phrase) and phrase not in text:
            findings.append(f"design-spec.md missing required source guidance: {phrase}")

    content_language = value_at(brief, "meta.content_language")
    if content_language == DEFAULT_CONTENT_LANGUAGE:
        if "用户可见 UI 文案必须使用简体中文" not in text:
            findings.append("design-spec.md missing Simplified Chinese output-language rule")
        if not language_checks.is_chinese_first_prompt(text):
            findings.append("design-spec.md declares zh-CN but is not Chinese-first")

    design_raw_path = value_at(brief, "design_system.design_md_path")
    design_path = resolve_existing_file(design_raw_path, [package_dir, Path.cwd()])
    if not design_path:
        findings.append(f"design_system.design_md_path does not resolve: {design_raw_path}")
    else:
        try:
            design_text = design_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            findings.append(f"DESIGN.md is not readable UTF-8: {error}")
            return
        except OSError as error:
            findings.append(f"DESIGN.md cannot be read: {error}")
            return
        design_label = export_design_spec.resolve_design_label_from_brief(
            brief,
            package_dir / "design-brief.json",
            design_path,
        )
        expected = export_design_spec.render_design_spec(
            brief,
            design_text,
            design_label=design_label,
        )
        if text != expected:
            findings.append("design-spec.md does not match export_design_spec.py output")


def normalize_inline_value(value):
    cleaned = value.strip()
    while cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def extract_review_section(text, review_name):
    heading = f"## {review_name}"
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return ""
    collected = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def parse_review_summary_fields(section):
    fields = {}
    for line in section.splitlines():
        stripped = line.strip()
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            if key in {"recommended_next_action", "reason", "next_copy_source"}:
                fields[key] = normalize_inline_value(value)
        if "：" in stripped:
            key, value = stripped.split("：", 1)
            key = key.strip()
            if key in {"原因", "reason"}:
                fields["reason"] = normalize_inline_value(value)
    return fields


def parse_review_option_rows(section):
    rows = {}
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [normalize_inline_value(cell) for cell in stripped.strip("|").split("|")]
        if len(cells) != 4:
            continue
        action = cells[0]
        if action in {"action", "---"} or action.startswith("---"):
            continue
        rows[action] = {
            "enabled": cells[1].lower(),
            "disabled_reason": cells[2],
            "next_copy_source": cells[3],
        }
    return rows


def check_review_section_matches_json(review_path, review, section, findings):
    relative = f"reviews/review-next-actions.md section {review_path.name}"
    next_actions = review.get("next_actions") if isinstance(review.get("next_actions"), dict) else {}
    fields = parse_review_summary_fields(section)
    recommended = next_actions.get("recommended_next_action")
    if has_text(recommended) and fields.get("recommended_next_action") != recommended:
        findings.append(f"{relative} recommended_next_action does not match JSON: {recommended}")
    reason = next_actions.get("reason")
    if has_text(reason) and fields.get("reason") != reason:
        findings.append(f"{relative} reason does not match JSON")

    options = next_actions.get("options")
    if not isinstance(options, list):
        return
    rows = parse_review_option_rows(section)
    for option in options:
        if not isinstance(option, dict):
            continue
        action = option.get("action")
        if not has_text(action):
            continue
        row = rows.get(action)
        if row is None:
            findings.append(f"{relative} missing option row: {action}")
            continue
        expected_enabled = str(option.get("enabled")).lower()
        if row["enabled"] != expected_enabled:
            findings.append(f"{relative} option {action} enabled does not match JSON")
        expected_disabled_reason = option.get("disabled_reason") or ""
        if row["disabled_reason"] != expected_disabled_reason:
            findings.append(f"{relative} option {action} disabled_reason does not match JSON")
        expected_next_copy_source = option.get("next_copy_source") or ""
        if row["next_copy_source"] != expected_next_copy_source:
            findings.append(f"{relative} option {action} next_copy_source does not match JSON")


def check_review_next_actions(package_dir, findings):
    reviews_dir = package_dir / "reviews"
    if not reviews_dir.exists():
        return
    review_jsons = sorted(reviews_dir.glob("result-review*.json"))
    if not review_jsons:
        return
    path = reviews_dir / "review-next-actions.md"
    text = read_text(path, findings, "reviews/review-next-actions.md")
    if not text:
        return
    for phrase in ["recommended_next_action", "direct_repair", "external_prompt", "revise_spec", "enabled", "disabled_reason"]:
        if phrase not in text:
            findings.append(f"reviews/review-next-actions.md missing next-action field: {phrase}")
    for review_path in review_jsons:
        if review_path.name not in text:
            findings.append(f"reviews/review-next-actions.md must reference {review_path.name}")
            continue
        review = load_json_object(review_path, findings, f"reviews/{review_path.name}")
        if not review:
            continue
        section = extract_review_section(text, review_path.name)
        if not section:
            findings.append(f"reviews/review-next-actions.md missing section for {review_path.name}")
            continue
        check_review_section_matches_json(review_path, review, section, findings)


def validate_package(package_dir, require_review=False):
    package_dir = Path(package_dir)
    findings = []
    if not package_dir.is_dir():
        return [f"missing directory: {package_dir}"]

    brief = load_json_object(package_dir / "design-brief.json", findings, "design-brief.json")
    start_text = read_text(package_dir / "START_HERE.md", findings, "START_HERE.md")
    spec_text = read_text(package_dir / "design-spec.md", findings, "design-spec.md")
    check_no_private_text("START_HERE.md", start_text, findings)
    check_no_private_text("design-spec.md", spec_text, findings)

    if start_text:
        check_start_here(start_text, findings)
    if spec_text and brief:
        check_design_spec(package_dir, spec_text, brief, findings)

    if require_review:
        check_review_next_actions(package_dir, findings)

    return findings


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate BriefPilot's user-facing package flow.")
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--require-review", action="store_true", help="Require review-next-actions.md when review JSON files exist.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    findings = validate_package(args.package_dir, require_review=args.require_review)
    if findings:
        print("invalid user-flow package:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"valid user-flow package: {args.package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
