#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
RAW_INPUT = "帮我做一个 AI 搜索产品官网"
REQUIRED_FILES = [
    "README.md",
    "index.html",
    "comparison-demo.json",
    "baseline-controlled.md",
    "briefpilot-enhanced.md",
    "future-real-output-todo.md",
]
CONTROLLED_SOURCE_TYPES = {"controlled", "simulated", "controlled_baseline"}
NAMED_TOOL_TOKENS = ["v0", "Lovable", "Bolt", "Figma Make", "Claude Design", "huashu-design"]
MATURITY_TERMS = ["受众", "结构", "证据", "评审"]
CHINESE_VISIBLE_TERMS = [
    "同一个模糊需求",
    "直接生成",
    "受控基线",
    "不是命名工具输出",
    "BriefPilot 强化结果",
    "受众",
    "结构",
    "证据",
    "评审",
]
PRIVATE_TOKENS = ["/" + "Users/", "Desktop/" + "project", "kang" + "jiaqi"]


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def value_at(data, dotted_path):
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def read_text(path, findings, label):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        findings.append(f"{label} missing file: {path}")
    except UnicodeDecodeError as exc:
        findings.append(f"{label} is not readable UTF-8 text: {exc}")
    except OSError as exc:
        findings.append(f"{label} cannot be read: {exc}")
    return ""


def load_json_object(path, findings, label):
    text = read_text(path, findings, label)
    if not text:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        findings.append(f"{label} invalid json: {exc}")
        return {}
    if not isinstance(data, dict):
        findings.append(f"{label} must be a JSON object")
        return {}
    return data


def resolve_repo_relative_path(raw_path, root, findings, field_name):
    if not has_text(raw_path):
        return None, False
    candidate = Path(raw_path)
    if candidate.is_absolute() or str(raw_path).startswith("~"):
        findings.append(f"{field_name} must be repo-relative")
        return None, True
    if ".." in candidate.parts:
        findings.append(f"{field_name} must not contain parent directory traversal")
        return None, True

    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        findings.append(f"{field_name} must stay within repository root")
        return None, True

    if not resolved.exists():
        return None, False
    return resolved, False


def check_required_files(demo_dir, findings):
    for relative in REQUIRED_FILES:
        if not (demo_dir / relative).is_file():
            findings.append(f"missing required file: {relative}")


def check_no_private_text(text_by_file, findings):
    for relative, text in text_by_file.items():
        for token in PRIVATE_TOKENS:
            if token in text:
                findings.append(f"{relative} contains forbidden local text: {token}")


def check_manifest(manifest, root, demo_dir, findings):
    if not has_text(manifest.get("schema_version")) or not str(manifest.get("schema_version")).startswith("1"):
        findings.append("comparison-demo.json schema_version must start with 1")
    if manifest.get("raw_input") != RAW_INPUT:
        findings.append("comparison-demo.json raw_input does not match the shared input")

    source_type = value_at(manifest, "baseline.source_type")
    if source_type not in CONTROLLED_SOURCE_TYPES:
        findings.append("baseline.source_type must be controlled or simulated")
    baseline_blob = " ".join(
        str(value_at(manifest, path) or "")
        for path in ["baseline.source_type", "baseline.label", "baseline.summary"]
    )
    if source_type not in CONTROLLED_SOURCE_TYPES or any(token.lower() in baseline_blob.lower() for token in NAMED_TOOL_TOKENS):
        findings.append("baseline must not claim a named-tool source in this first version")

    enhanced_path = value_at(manifest, "enhanced.source_path")
    resolved_enhanced, invalid_enhanced_path = resolve_repo_relative_path(
        enhanced_path,
        root,
        findings,
        "enhanced.source_path",
    )
    expected_enhanced = (root / "examples" / "ai-search-landing").resolve()
    if not invalid_enhanced_path and not resolved_enhanced:
        findings.append(f"enhanced.source_path does not resolve: {enhanced_path}")
    elif resolved_enhanced and resolved_enhanced != expected_enhanced:
        findings.append("enhanced.source_path must resolve to examples/ai-search-landing")

    page_path = value_at(manifest, "page.path")
    resolved_page, invalid_page_path = resolve_repo_relative_path(
        page_path,
        root,
        findings,
        "page.path",
    )
    expected_page = (demo_dir / "index.html").resolve()
    if not invalid_page_path and (not resolved_page or resolved_page != expected_page):
        findings.append("page.path must resolve to examples/comparison-demo/index.html")
    if value_at(manifest, "page.offline_safe") is not True:
        findings.append("page.offline_safe must be true")

    baseline_region = value_at(manifest, "visual_mockups.baseline_region")
    enhanced_region = value_at(manifest, "visual_mockups.enhanced_region")
    if baseline_region != "baseline-mockup":
        findings.append("visual_mockups.baseline_region must be baseline-mockup")
    if enhanced_region != "briefpilot-mockup":
        findings.append("visual_mockups.enhanced_region must be briefpilot-mockup")

    claims = manifest.get("comparison_claims")
    if not isinstance(claims, list) or len([claim for claim in claims if has_text(claim)]) < 4:
        findings.append("comparison_claims must contain at least four concrete claims")
    elif sum(1 for claim in claims if any(term in claim for term in MATURITY_TERMS)) < 4:
        findings.append("comparison_claims must describe Chinese maturity terms: 受众, 结构, 证据, 评审")

    todo_path = value_at(manifest, "future_real_output_todo_path")
    resolved_todo, invalid_todo_path = resolve_repo_relative_path(
        todo_path,
        root,
        findings,
        "future_real_output_todo_path",
    )
    expected_todo = (demo_dir / "future-real-output-todo.md").resolve()
    if not invalid_todo_path and (not resolved_todo or resolved_todo != expected_todo):
        findings.append("future_real_output_todo_path must resolve to future-real-output-todo.md")


def check_html(html, manifest, findings):
    html_lower = html.lower()
    if 'lang="zh-cn"' not in html_lower:
        findings.append('index.html html lang must be "zh-CN"')

    required_text = [
        RAW_INPUT,
        "直接生成的受控基线",
        "BriefPilot 强化结果",
        "受控基线示例",
        "不是命名工具输出",
    ]
    for text in required_text:
        if text.lower() not in html_lower:
            findings.append(f"index.html missing required text: {text}")

    for term in MATURITY_TERMS:
        if term not in html:
            findings.append(f"index.html missing maturity difference term: {term}")

    visible_term_count = sum(1 for term in CHINESE_VISIBLE_TERMS if term in html)
    if visible_term_count < 7:
        findings.append("index.html must contain visible Chinese-first comparison copy beyond the raw input")

    for path in ["visual_mockups.baseline_region", "visual_mockups.enhanced_region"]:
        region = value_at(manifest, path)
        if has_text(region) and f'data-demo-region="{region}"' not in html:
            findings.append(f"index.html missing visual mockup marker: {region}")

    h1_count = html_lower.count("<h1")
    if h1_count != 1:
        findings.append("index.html must contain exactly one h1")

    if "http://" in html_lower or "https://" in html_lower:
        findings.append("index.html must not include remote asset or script dependencies")


def check_baseline_content(text, findings):
    text_lower = text.lower()
    if ("受控" not in text and "controlled" not in text_lower) or ("不是命名工具" not in text and "not captured from a named" not in text_lower):
        findings.append("baseline-controlled.md must label the baseline as controlled and not captured from a named tool")
    for token in NAMED_TOOL_TOKENS:
        if token.lower() in text_lower:
            findings.append("baseline-controlled.md must not name downstream tools as the baseline source")


def check_enhanced_content(text, findings):
    required = ["examples/ai-search-landing", "企业信任", "来源", "评审"]
    for token in required:
        if token.lower() not in text.lower():
            findings.append(f"briefpilot-enhanced.md missing grounded detail: {token}")


def check_future_todo(text, findings):
    for token in ["v0", "Lovable", "Bolt", "Figma Make", "记录日期", "完整提示词", "是否编辑"]:
        if token.lower() not in text.lower():
            findings.append(f"future-real-output-todo.md missing capture detail: {token}")


def check_readme(root, findings):
    readme = read_text(root / "README.md", findings, "root README.md")
    link_targets = [
        "(examples/comparison-demo/index.html)",
        "(./examples/comparison-demo/index.html)",
    ]
    if not any(target in readme for target in link_targets):
        findings.append("README.md must link to examples/comparison-demo/index.html")


def validate(root, demo_dir):
    root = Path(root).resolve()
    demo_dir = Path(demo_dir)
    if not demo_dir.is_absolute():
        demo_dir = root / demo_dir
    demo_dir = demo_dir.resolve()

    findings = []
    if not demo_dir.is_dir():
        return [f"missing directory: {demo_dir}"]

    check_required_files(demo_dir, findings)

    text_by_file = {}
    for relative in REQUIRED_FILES:
        path = demo_dir / relative
        if path.is_file() and path.suffix in {".md", ".html"}:
            text_by_file[relative] = read_text(path, findings, relative)
    check_no_private_text(text_by_file, findings)

    manifest = load_json_object(demo_dir / "comparison-demo.json", findings, "comparison-demo.json")
    if manifest:
        check_manifest(manifest, root, demo_dir, findings)

    html = text_by_file.get("index.html", "")
    if html and manifest:
        check_html(html, manifest, findings)

    baseline = text_by_file.get("baseline-controlled.md", "")
    if baseline:
        check_baseline_content(baseline, findings)

    enhanced = text_by_file.get("briefpilot-enhanced.md", "")
    if enhanced:
        check_enhanced_content(enhanced, findings)

    future = text_by_file.get("future-real-output-todo.md", "")
    if future:
        check_future_todo(future, findings)

    check_readme(root, findings)
    return findings


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate the BriefPilot comparison demo.")
    parser.add_argument("demo_dir", type=Path, help="Comparison demo directory.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    findings = validate(args.root, args.demo_dir)
    if findings:
        print("invalid comparison demo:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"valid: {args.demo_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
