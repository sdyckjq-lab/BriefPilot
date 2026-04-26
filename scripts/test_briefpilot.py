import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import check_design_md as design_md_report
import language_checks
import validate_golden_demo


ROOT = SCRIPTS_DIR.parents[0]
EXAMPLE_DIR = ROOT / "examples" / "ai-search-landing"
EXAMPLE = EXAMPLE_DIR / "design-brief.json"
DESIGN_MD = EXAMPLE_DIR / "DESIGN.md"
WORKSPACE_DIR = ROOT / "examples" / "ai-search-workspace"
WORKSPACE_EXAMPLE = WORKSPACE_DIR / "design-brief.json"
WORKSPACE_DESIGN_MD = WORKSPACE_DIR / "DESIGN.md"
COMPARISON_DIR = ROOT / "examples" / "comparison-demo"
VALIDATE_REVIEW = ROOT / "scripts" / "validate_result_review.py"
VALIDATE_COMPARISON = ROOT / "scripts" / "validate_comparison_demo.py"
EXPORT_MODIFICATION = ROOT / "scripts" / "export_modification_prompt.py"
STYLE_INDEX = ROOT / "references" / "design-style-index.json"
CHECK_DESIGN_MD = ROOT / "scripts" / "check_design_md.py"
VALIDATE_PUBLIC_PACKAGE = ROOT / "scripts" / "validate_public_package.py"
DESIGN_MD_FIXTURES = ROOT / "examples" / "design-md-fixtures"


def write_review_package(tmp):
    package = Path(tmp)
    (package / "DESIGN.md").write_text(
        """# Workspace DESIGN.md

Use restrained blue accents, dense but readable panels, 8px default radius, clear source-link focus states, and no decorative AI glow.
""",
        encoding="utf-8",
    )
    brief = {
        "meta": {"version": "0.1", "created_by": "BriefPilot", "content_language": "zh-CN", "target_tools": ["huashu-design", "claude-design", "v0"]},
        "project": {"name": "Workspace Detail", "summary": "AI search answer detail app page", "task_type": "app_page", "stage": "test"},
        "audience": {"primary_user": "research teams"},
        "goals": {"business_goal": "increase answer trust", "design_goal": "make answer sources clear"},
        "message": {"core_claim": "Review sourced AI answers with confidence."},
        "structure": {"sections": ["search", "answer", "sources"], "interaction_contract": ["Open source drawer"], "responsive_accessibility": ["Mobile source stack"]},
        "visual": {"strategy_name": "Dense Research Workspace"},
        "strategy_options": [{"name": "Dense Research Workspace", "selected": True}],
        "design_system": {"design_md_path": "DESIGN.md"},
        "quality_bar": {"review_criteria": ["source visibility"]},
        "assumptions": ["No screenshots provided."],
    }
    (package / "design-brief.json").write_text(json.dumps(brief), encoding="utf-8")
    (package / "generated.html").write_text("<main>answer with weak source cards</main>", encoding="utf-8")
    (package / "empty.md").write_text("   ", encoding="utf-8")
    (package / "generated.png").write_text("not really an image", encoding="utf-8")
    (package / "brief-revision.md").write_text("# Brief Revision\n\nAdd source disagreement recovery.", encoding="utf-8")
    (package / "other-DESIGN.md").write_text("# Other DESIGN.md\n\nWrong package.", encoding="utf-8")
    return package


def base_review(**overrides):
    review = {
        "schema_version": "1.0",
        "source": {"brief_path": "design-brief.json", "design_md_path": "DESIGN.md"},
        "target_tool": "generic",
        "evidence": {
            "kind": "pasted_summary",
            "summary": "The result has the right answer-detail layout but source cards are too muted.",
        },
        "decision": "tweak",
        "selected_strategy": "Dense Research Workspace",
        "strategy_preserved": True,
        "strengths": ["The answer area and query input are present."],
        "findings": [
            {
                "severity": "medium",
                "brief_reference": "quality_bar.review_criteria: source visibility",
                "issue": "Source cards are visually weaker than the answer.",
                "evidence": "Pasted result summary says sources are hard to notice.",
                "recommended_change": "Increase source card hierarchy and interaction affordance.",
            }
        ],
        "visual_review": {
            "status": "unavailable",
            "notes": "No inspectable screenshot was available; review used pasted summary fallback.",
        },
        "prompt_intent": "targeted_modification",
        "prompt": {
            "keep": ["Keep the Dense Research Workspace strategy."],
            "change": ["Make source cards visible and clickable."],
            "do_not_change": ["Do not change the approved visual system."],
            "acceptance_checks": ["Source cards are visible without competing with the answer."],
        },
    }
    for key, value in overrides.items():
        review[key] = value
    return review


def write_review(path, review):
    path.write_text(json.dumps(review, indent=2), encoding="utf-8")
    return path


def init_public_package_repo(tmp, gitignore=None):
    root = Path(tmp)
    subprocess.run(["git", "-C", str(root), "init"], text=True, capture_output=True, check=True)
    (root / ".gitignore").write_text(
        gitignore
        if gitignore is not None
        else "/AGENTS.md\n/docs/\n/需求文档/\n",
        encoding="utf-8",
    )
    (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (root / "README.md").write_text("# BriefPilot\n\nRun `scripts/export_prompt.py`.\n", encoding="utf-8")
    (root / "SKILL.md").write_text("# BriefPilot Skill\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(root), "add", ".gitignore", "LICENSE", "README.md", "SKILL.md"],
        text=True,
        capture_output=True,
        check=True,
    )
    return root


def run_public_package_validator(root):
    return subprocess.run(
        [sys.executable, str(VALIDATE_PUBLIC_PACKAGE), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


def write_comparison_demo(root):
    root = Path(root)
    demo = root / "examples" / "comparison-demo"
    demo.mkdir(parents=True)
    (root / "examples" / "ai-search-landing").mkdir(parents=True)
    (root / "README.md").write_text(
        "# BriefPilot\n\nOpen [comparison demo](examples/comparison-demo/index.html).\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "1.0",
        "raw_input": "帮我做一个 AI 搜索产品官网",
        "baseline": {
            "source_type": "controlled",
            "label": "直接生成的受控基线",
            "summary": "受控基线示例。",
        },
        "enhanced": {
            "label": "BriefPilot 强化结果",
            "source_path": "examples/ai-search-landing",
            "summary": "基于已验证样例。",
        },
        "page": {"path": "examples/comparison-demo/index.html", "offline_safe": True},
        "visual_mockups": {
            "baseline_region": "baseline-mockup",
            "enhanced_region": "briefpilot-mockup",
        },
        "comparison_claims": [
            "BriefPilot 补齐受众。",
            "BriefPilot 补齐结构。",
            "BriefPilot 补齐证据。",
            "BriefPilot 补齐评审标准。",
        ],
        "future_real_output_todo_path": "examples/comparison-demo/future-real-output-todo.md",
    }
    (demo / "comparison-demo.json").write_text(json.dumps(manifest), encoding="utf-8")
    (demo / "index.html").write_text(
        """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Comparison</title></head>
<body>
<h1>同一个模糊需求，结果质量不同</h1>
<p>帮我做一个 AI 搜索产品官网</p>
<section><h2>直接生成的受控基线</h2><p>受控基线示例，不是命名工具输出。</p><div data-demo-region="baseline-mockup">受众 结构 证据 评审 直接生成</div></section>
<section><h2>BriefPilot 强化结果</h2><div data-demo-region="briefpilot-mockup">受众 结构 证据 评审</div></section>
</body>
</html>
""",
        encoding="utf-8",
    )
    (demo / "baseline-controlled.md").write_text(
        "这是受控基线，不是命名工具输出，也不是从某个下游工具截取。\n",
        encoding="utf-8",
    )
    (demo / "briefpilot-enhanced.md").write_text(
        "基于 examples/ai-search-landing，包含企业信任策略、来源证据和评审标准。\n",
        encoding="utf-8",
    )
    (demo / "future-real-output-todo.md").write_text(
        "待采集：v0、Lovable、Bolt、Figma Make。记录日期、完整提示词和生成后是否编辑。\n",
        encoding="utf-8",
    )
    (demo / "README.md").write_text("# Demo\n\nOpen index.html.\n", encoding="utf-8")
    return demo


def run_comparison_validator(root, demo):
    return subprocess.run(
        [sys.executable, str(VALIDATE_COMPARISON), str(demo), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


class BriefPilotScriptTests(unittest.TestCase):
    def test_style_index_contract_and_docs(self):
        payload = json.loads(STYLE_INDEX.read_text(encoding="utf-8"))
        directions = payload.get("directions", [])
        expected_ids = {
            "ai_product_landing_page",
            "developer_tool",
            "enterprise_data_workspace",
            "documentation_knowledge_base",
            "finance_payments",
            "creation_tool",
            "consumer_app",
            "commerce_brand_retail",
            "media_editorial",
            "productivity_tool",
            "collaboration_workflow",
            "premium_visual_showcase",
        }
        self.assertEqual({item.get("id") for item in directions}, expected_ids)
        self.assertEqual(len(directions), 12)
        for item in directions:
            self.assertTrue(item.get("suitable_task_types"), item.get("id"))
            self.assertTrue(item.get("source_links"), item.get("id"))
            self.assertTrue(item.get("source_license"), item.get("id"))
            self.assertTrue(item.get("attribution"), item.get("id"))
            self.assertTrue(item.get("usage_boundary"), item.get("id"))
            self.assertTrue(item.get("brand_copy_boundary"), item.get("id"))
            self.assertTrue(item.get("drift_checks"), item.get("id"))
            for link in item.get("source_links", []):
                self.assertTrue(link.get("source_license"), item.get("id"))
                self.assertTrue(link.get("attribution"), item.get("id"))
                self.assertTrue(link.get("usage_boundary"), item.get("id"))

        style_doc = (ROOT / "references" / "design-style-index.md").read_text(encoding="utf-8")
        quality_doc = (ROOT / "references" / "design-md-quality-rules.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "workflow.md").read_text(encoding="utf-8")
        design_doc = (ROOT / "references" / "design-md.md").read_text(encoding="utf-8")
        self.assertIn("Reference mechanisms, do not copy brands", style_doc)
        self.assertIn("does not treat `awesome-design-md` as an official Google source", style_doc)
        self.assertIn("component states", quality_doc.lower())
        self.assertIn("references/design-style-index.md", skill)
        self.assertIn("references/design-md-quality-rules.md", skill)
        self.assertIn("design-style-index.json", workflow)
        self.assertIn("design-style-index.json", design_doc)

    def test_validate_example_brief(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_brief.py"), str(EXAMPLE)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("valid", result.stdout.lower())

    def test_language_checks_reject_english_heavy_zh_cn_content(self):
        english_brief = {
            "meta": {"content_language": "zh-CN"},
            "project": {"summary": "English product brief. " * 80},
            "audience": {"primary_user": "knowledge workers " * 60},
            "goals": {"business_goal": "drive signup " * 60},
        }
        chinese_brief = {
            "meta": {"content_language": "zh-CN"},
            "project": {"summary": "这是面向中文用户的产品说明。" * 80},
            "audience": {"primary_user": "知识工作者和小团队需要跨工作资料查找可信答案。" * 40},
            "goals": {"business_goal": "推动试用注册并让用户理解产品价值。" * 40},
        }
        self.assertFalse(language_checks.is_chinese_first_brief(english_brief))
        self.assertTrue(language_checks.is_chinese_first_brief(chinese_brief))
        self.assertFalse(language_checks.is_chinese_first_prompt("Use Simplified Chinese.\n" + "English prompt body. " * 300))
        self.assertTrue(language_checks.is_chinese_first_prompt("用户可见 UI 文案必须使用简体中文。\n" + "中文提示词正文。" * 300))
        self.assertFalse(language_checks.is_chinese_first_review(base_review()))
        chinese_review = json.loads((WORKSPACE_DIR / "reviews" / "result-review-pasted-summary.json").read_text(encoding="utf-8"))
        self.assertTrue(language_checks.is_chinese_first_review(chinese_review))

    def test_validate_example_design_md(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_design_md.py"), str(DESIGN_MD)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("valid", result.stdout.lower())

    def test_design_md_checker_blocks_core_failures_and_allows_warnings(self):
        valid_text = DESIGN_MD.read_text(encoding="utf-8")
        cases = [
            ("missing_front_matter.md", "# No front matter\n\n## Overview\nText", False, "Missing YAML front matter"),
            ("broken_reference.md", valid_text.replace("{colors.primary_action}", "{colors.missing}", 1), False, "Broken token reference"),
            ("bad_color.md", valid_text.replace('primary_action: "#2563EB"', 'primary_action: "blue"', 1), False, "Invalid required color"),
            ("brand_copy.md", valid_text + "\n\nCopy Linear's logo and exact brand identity.\n", False, "Direct brand-copy instruction"),
            ("warning_only.md", valid_text.replace("default blue, hover darker blue, pressed compact shadow, disabled muted border, loading spinner with unchanged width, success confirmation, error retry message, and visible focus ring", "clear state guidance"), True, "valid"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for filename, text, should_pass, expected in cases:
                path = Path(tmp) / filename
                path.write_text(text, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "validate_design_md.py"), str(path)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if should_pass:
                    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0, filename)
                self.assertIn(expected, result.stdout + result.stderr)

    def test_check_design_md_writes_fallback_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            markdown_out = Path(tmp) / "design-md-review.md"
            json_out = Path(tmp) / "design-md-review.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_DESIGN_MD),
                    str(DESIGN_MD),
                    "--mode",
                    "fallback",
                    "--markdown-out",
                    str(markdown_out),
                    "--json-out",
                    str(json_out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(json_out.read_text(encoding="utf-8"))
            markdown = markdown_out.read_text(encoding="utf-8")
            self.assertEqual(report["mode"], "briefpilot_fallback")
            self.assertFalse(report["blocking"])
            self.assertEqual(report["reference_direction"]["id"], "ai_product_landing_page")
            self.assertIn("模式：briefpilot_fallback", markdown)
            self.assertIn("是否阻断：false", markdown)
            self.assertIn("参考方向：ai_product_landing_page", markdown)
            self.assertIn(f"- blocking: {report['summary']['blocking']}", markdown)
            self.assertIn(f"- warning: {report['summary']['warning']}", markdown)
            self.assertIn(f"- info: {report['summary']['info']}", markdown)
            self.assertIn(f"下一步：{report['next_action']}", markdown)
            self.assertIn("source_sha256", report)
            self.assertIn("来源 SHA-256：", markdown)

    def test_design_review_report_detects_design_md_content_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            design_path = package / "DESIGN.md"
            design_path.write_text(DESIGN_MD.read_text(encoding="utf-8"), encoding="utf-8")
            review_dir = package / "reviews"
            review_dir.mkdir()
            report = design_md_report.build_report(design_path.resolve(), requested_mode="fallback", official_command=None)
            design_md_report.write_report(
                report,
                review_dir / "design-md-review.md",
                review_dir / "design-md-review.json",
            )
            design_path.write_text(design_path.read_text(encoding="utf-8") + "\n\nContent-only drift.\n", encoding="utf-8")

            findings = []
            validate_golden_demo.check_design_review_report(
                package,
                {
                    "design_system": {
                        "design_md_path": "DESIGN.md",
                        "reference_direction": {"id": "ai_product_landing_page"},
                    }
                },
                findings,
            )
            self.assertIn("reviews/design-md-review.json does not match forced fallback checker output", findings)

    def test_copied_landing_demo_detects_design_md_content_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "landing"
            shutil.copytree(EXAMPLE_DIR, package)
            design_path = package / "DESIGN.md"
            design_path.write_text(design_path.read_text(encoding="utf-8") + "\n\nCopied package drift.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_golden_demo.py"), str(package)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reviews/design-md-review.json does not match forced fallback checker output", result.stdout + result.stderr)

    def test_design_review_report_blocks_invalid_regenerated_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            design_path = package / "DESIGN.md"
            design_path.write_text(
                DESIGN_MD.read_text(encoding="utf-8").replace('primary_action: "#2563EB"', 'primary_action: "blue"', 1),
                encoding="utf-8",
            )
            review_dir = package / "reviews"
            review_dir.mkdir()
            report = design_md_report.build_report(design_path.resolve(), requested_mode="fallback", official_command=None)
            design_md_report.write_report(
                report,
                review_dir / "design-md-review.md",
                review_dir / "design-md-review.json",
            )

            findings = []
            validate_golden_demo.check_design_review_report(
                package,
                {
                    "design_system": {
                        "design_md_path": "DESIGN.md",
                        "reference_direction": {"id": "ai_product_landing_page"},
                    }
                },
                findings,
            )
            self.assertIn("DESIGN.md fallback report has blocking findings", findings)

    def test_check_design_md_official_path_is_trust_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "dir"
            directory.mkdir()
            non_md = Path(tmp) / "DESIGN.txt"
            non_md.write_text("text", encoding="utf-8")
            absolute_npx = Path(tmp) / "npx"
            absolute_npx.write_text("#!/bin/sh\necho npx\n", encoding="utf-8")
            absolute_npx.chmod(0o755)
            safe_name_symlink = Path(tmp) / "safe-google-lint"
            safe_name_symlink.symlink_to(absolute_npx)
            cases = [
                ([str(CHECK_DESIGN_MD), str(DESIGN_MD), "--mode", "official"], "official mode requires --official-command"),
                ([str(CHECK_DESIGN_MD), str(DESIGN_MD), "--official-command", "npx"], "absolute path"),
                ([str(CHECK_DESIGN_MD), str(DESIGN_MD), "--official-command", str(absolute_npx)], "package manager"),
                ([str(CHECK_DESIGN_MD), str(DESIGN_MD), "--official-command", str(safe_name_symlink)], "package manager"),
                ([str(CHECK_DESIGN_MD), str(directory)], "not a directory"),
                ([str(CHECK_DESIGN_MD), str(non_md)], "must end in .md"),
            ]
            for args, expected in cases:
                result = subprocess.run(
                    [sys.executable, *args],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0, expected)
                self.assertIn(expected, result.stdout + result.stderr)

    def test_fallback_mode_ignores_official_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = Path(tmp) / "fake-google-lint"
            command.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = \"--version\" ]; then echo fake-google-lint; exit 0; fi\n"
                "echo should-not-run >&2\n"
                "exit 2\n",
                encoding="utf-8",
            )
            command.chmod(0o755)
            json_out = Path(tmp) / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_DESIGN_MD),
                    str(DESIGN_MD),
                    "--mode",
                    "fallback",
                    "--official-command",
                    str(command),
                    "--json-out",
                    str(json_out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "briefpilot_fallback")
            self.assertFalse(report["official_tool"]["available"])
            self.assertFalse(report["official_tool"]["merged"])
            self.assertNotIn("should-not-run", json.dumps(report))

    def test_official_command_output_is_capped(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = Path(tmp) / "fake-google-lint"
            command.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "if sys.argv[1:] == ['--version']:\n"
                "    print('fake-google-lint')\n"
                "else:\n"
                "    sys.stdout.write('x' * 10000)\n",
                encoding="utf-8",
            )
            command.chmod(0o755)
            json_out = Path(tmp) / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_DESIGN_MD),
                    str(DESIGN_MD),
                    "--mode",
                    "auto",
                    "--official-command",
                    str(command),
                    "--json-out",
                    str(json_out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertIn(result.returncode, {0, 1}, result.stderr + result.stdout)
            report = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertIn("[truncated]", report["official_tool"]["raw_output"])
            self.assertLessEqual(len(report["official_tool"]["raw_output"]), design_md_report.RAW_OUTPUT_LIMIT + len("\n[truncated]"))

    def test_official_command_receives_minimal_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = Path(tmp) / "fake-google-lint"
            command.write_text(
                "#!/usr/bin/env python3\n"
                "import os, sys\n"
                "if sys.argv[1:] == ['--version']:\n"
                "    print('fake-google-lint')\n"
                "else:\n"
                "    print(os.environ.get('BRIEFPILOT_SECRET_PROBE', 'missing'))\n",
                encoding="utf-8",
            )
            command.chmod(0o755)
            json_out = Path(tmp) / "report.json"
            previous = os.environ.get("BRIEFPILOT_SECRET_PROBE")
            os.environ["BRIEFPILOT_SECRET_PROBE"] = "leaked-secret"
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(CHECK_DESIGN_MD),
                        str(DESIGN_MD),
                        "--mode",
                        "auto",
                        "--official-command",
                        str(command),
                        "--json-out",
                        str(json_out),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
            finally:
                if previous is None:
                    os.environ.pop("BRIEFPILOT_SECRET_PROBE", None)
                else:
                    os.environ["BRIEFPILOT_SECRET_PROBE"] = previous
            self.assertIn(result.returncode, {0, 1}, result.stderr + result.stdout)
            report = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertIn("missing", report["official_tool"]["raw_output"])
            self.assertNotIn("leaked-secret", json.dumps(report))

    def test_required_color_roles_must_be_hex_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            boolean_color = Path(tmp) / "boolean-color.md"
            boolean_color.write_text(
                DESIGN_MD.read_text(encoding="utf-8").replace('primary_action: "#2563EB"', "primary_action: true", 1),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_design_md.py"), str(boolean_color)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid required color", result.stdout + result.stderr)

    def test_design_md_report_markdown_escapes_finding_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            unsafe_design = Path(tmp) / "unsafe.md"
            unsafe_design.write_text(
                DESIGN_MD.read_text(encoding="utf-8").replace(
                    'primary_action: "#2563EB"',
                    'primary_action: "<img src=x onerror=alert(1)>"',
                    1,
                ),
                encoding="utf-8",
            )
            markdown_out = Path(tmp) / "report.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_DESIGN_MD),
                    str(unsafe_design),
                    "--mode",
                    "fallback",
                    "--markdown-out",
                    str(markdown_out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            markdown = markdown_out.read_text(encoding="utf-8")
            self.assertNotIn("<img src=x onerror=alert(1)>", markdown)
            self.assertIn("&lt;img src=x onerror=alert(1)&gt;", markdown)

    def test_validate_design_md_handles_non_utf8_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_bytes(b"\xff\xfe\x00")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_design_md.py"), str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not readable UTF-8", result.stdout + result.stderr)

    def test_design_md_fixtures_cover_fallback_severity(self):
        cases = [
            ("valid-upgraded", True, None),
            ("broken-reference", False, "Broken token reference"),
            ("missing-states", True, "missing_component_state"),
            ("direction-drift", True, "reference_direction_drift"),
            ("brand-copy-risk", False, "brand-copy"),
            ("bad-color", False, "Invalid required color"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for fixture_name, should_validate, expected in cases:
                design_path = DESIGN_MD_FIXTURES / fixture_name / "DESIGN.md"
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "validate_design_md.py"), str(design_path)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if should_validate:
                    self.assertEqual(result.returncode, 0, fixture_name + result.stderr + result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0, fixture_name)
                    self.assertIn(expected, result.stdout + result.stderr)

                markdown_out = Path(tmp) / f"{fixture_name}.md"
                json_out = Path(tmp) / f"{fixture_name}.json"
                report = subprocess.run(
                    [
                        sys.executable,
                        str(CHECK_DESIGN_MD),
                        str(design_path),
                        "--mode",
                        "fallback",
                        "--markdown-out",
                        str(markdown_out),
                        "--json-out",
                        str(json_out),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                report_payload = json.loads(json_out.read_text(encoding="utf-8"))
                self.assertEqual(report.returncode == 0, not report_payload["blocking"], fixture_name)
                markdown = markdown_out.read_text(encoding="utf-8")
                self.assertIn(f"是否阻断：{str(report_payload['blocking']).lower()}", markdown)
                self.assertIn(f"- warning: {report_payload['summary']['warning']}", markdown)
                if expected and should_validate:
                    self.assertIn(expected, json.dumps(report_payload))

    def test_optional_official_tool_test_runs_only_with_safe_command(self):
        command = os.environ.get("BRIEFPILOT_GOOGLE_DESIGN_MD_COMMAND")
        if not command:
            self.skipTest("Set BRIEFPILOT_GOOGLE_DESIGN_MD_COMMAND to a safe absolute local command to exercise official lint.")
        if not Path(command).is_absolute():
            self.skipTest("Official command env var is not an absolute path.")
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_DESIGN_MD),
                str(DESIGN_MD),
                "--mode",
                "auto",
                "--official-command",
                command,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertIn(result.returncode, {0, 1})

    def test_upgraded_example_design_md_assets(self):
        index_ids = {item["id"] for item in json.loads(STYLE_INDEX.read_text(encoding="utf-8"))["directions"]}
        for example_dir in [EXAMPLE_DIR, WORKSPACE_DIR]:
            design_text = (example_dir / "DESIGN.md").read_text(encoding="utf-8")
            brief = json.loads((example_dir / "design-brief.json").read_text(encoding="utf-8"))
            for heading in [
                "## Overview",
                "## Visual Theme",
                "## Colors",
                "## Typography",
                "## Layout",
                "## Elevation & Depth",
                "## Shapes",
                "## Components",
                "## Responsive Behavior",
                "## Motion & Feedback",
                "## Content Voice",
                "## Do's and Don'ts",
                "## Reference Direction",
                "## Agent Guidance",
            ]:
                self.assertIn(heading, design_text, example_dir.name)
            for phrase in ["background:", "surface:", "primary_action:", "danger:", "display:", "caption:", "components:"]:
                self.assertIn(phrase, design_text, example_dir.name)
            for phrase in ["keyboard", "focus", "44px", "reduced motion", "loading", "empty", "success", "error"]:
                self.assertIn(phrase, design_text.lower(), example_dir.name)
            direction = brief.get("design_system", {}).get("reference_direction", {})
            self.assertIn(direction.get("id"), index_ids)
            self.assertIn(direction.get("id"), design_text)

    def test_design_md_quality_proofs_exist(self):
        for example_dir in [EXAMPLE_DIR, WORKSPACE_DIR]:
            proof = (example_dir / "design-md-quality-proof.md").read_text(encoding="utf-8")
            for phrase in ["更强的 token 骨架", "更完整的状态说明", "更清楚的可访问性指导", "更强的参考边界"]:
                self.assertIn(phrase, proof)
            self.assertIn("提示词就绪证明", proof)

    def test_score_example_brief(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "score_brief.py"), str(EXAMPLE)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(payload["score"], 81)
        self.assertEqual(payload["level"], "strong")
        self.assertIn("gaps", payload)
        self.assertIn("risks", payload)
        self.assertIn("recommended_next_step", payload)

    def test_score_thin_brief_is_not_strong(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "thin.json"
            brief.write_text(
                json.dumps(
                    {
                        "audience": {"primary_user": "teams"},
                        "goals": {"business_goal": "drive signup"},
                        "message": {"core_claim": "Search work faster."},
                        "structure": {"sections": ["hero"]},
                        "visual": {"strategy_name": "Trust"},
                        "design_system": {"design_md_path": "missing-DESIGN.md"},
                        "constraints": {"responsive": True},
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "score_brief.py"), str(brief)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertLess(payload["score"], 81)
            self.assertNotEqual(payload["level"], "strong")
            self.assertTrue(payload["gaps"])

    def test_validate_brief_rejects_missing_design_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.json"
            brief.write_text(
                json.dumps(
                    {
                        "meta": {"version": "0.1", "created_by": "BriefPilot", "content_language": "zh-CN"},
                        "project": {"name": "Missing Design", "summary": "Example", "task_type": "saas_website"},
                        "audience": {"primary_user": "teams"},
                        "goals": {"business_goal": "signup", "design_goal": "clarity"},
                        "message": {"core_claim": "Search work faster."},
                        "structure": {"sections": ["hero"]},
                        "visual": {"strategy_name": "Trust"},
                        "design_system": {"design_md_path": "missing-DESIGN.md"},
                        "quality_bar": {"review_criteria": ["clarity"]},
                        "assumptions": ["No real assets were provided."],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_brief.py"), str(brief)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("design_system.design_md_path", result.stdout)

    def test_validate_brief_rejects_english_heavy_zh_cn_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            (package / "DESIGN.md").write_text("# DESIGN.md\n\n## Overview\n", encoding="utf-8")
            brief = package / "brief.json"
            brief.write_text(
                json.dumps(
                    {
                        "meta": {"version": "0.1", "created_by": "BriefPilot", "content_language": "zh-CN"},
                        "project": {"name": "Search Landing", "summary": "English product brief. " * 120, "task_type": "saas_website"},
                        "audience": {"primary_user": "knowledge workers " * 60},
                        "goals": {"business_goal": "drive trial signup " * 60, "design_goal": "make the value proposition clear " * 60},
                        "message": {"core_claim": "Search work faster with reliable answers." * 40},
                        "structure": {"sections": ["hero", "workflow", "security"]},
                        "visual": {"strategy_name": "Enterprise Trust"},
                        "design_system": {"design_md_path": "DESIGN.md"},
                        "quality_bar": {"review_criteria": ["clear CTA", "source proof"]},
                        "assumptions": ["No real product screenshots were provided."],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_brief.py"), str(brief)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("brief values are not Chinese-first", result.stdout)

    def test_validate_golden_demo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_golden_demo.py"), str(EXAMPLE_DIR)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("valid", result.stdout.lower())

    def test_validate_workspace_brief_and_design_md(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_brief.py"), str(WORKSPACE_EXAMPLE)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_design_md.py"), str(WORKSPACE_DESIGN_MD)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_validate_review_demo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_review_demo.py"), str(WORKSPACE_DIR)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("valid", result.stdout.lower())

    def test_validate_review_demo_rejects_english_review_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "ai-search-workspace"
            shutil.copytree(WORKSPACE_DIR, copied)
            report = design_md_report.build_report((copied / "DESIGN.md").resolve(), requested_mode="fallback", official_command=None)
            design_md_report.write_report(
                report,
                copied / "reviews" / "design-md-review.md",
                copied / "reviews" / "design-md-review.json",
            )

            review_path = copied / "reviews" / "result-review-pasted-summary.json"
            review = json.loads(review_path.read_text(encoding="utf-8"))
            review["evidence"]["summary"] = "The generated workspace includes a search box and answer panel, but source cards are visually weak and hard to connect to citations."
            review["strengths"] = ["The main answer layout is present.", "The saved and share actions are visible."]
            review["findings"] = [
                {
                    "severity": "medium",
                    "brief_reference": "quality_bar.review_criteria: source visibility",
                    "issue": "Source cards are too quiet compared with the answer panel.",
                    "evidence": "The pasted summary says source cards are difficult to notice.",
                    "recommended_change": "Increase source card hierarchy and show a clearer selected state.",
                }
            ]
            review["visual_review"]["notes"] = "No screenshot was available; the review used the pasted summary as fallback evidence."
            review["prompt"] = {
                "keep": ["Keep the dense research workspace strategy."],
                "change": ["Make source cards more visible and connect citations to matching cards."],
                "do_not_change": ["Do not change the approved visual system."],
                "acceptance_checks": ["Source cards are visible without competing with the answer."],
            }
            review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            markdown = copied / "reviews" / "result-review-pasted-summary.md"
            markdown.write_text(
                "\n".join(
                    [
                        "# Result Review",
                        "",
                        "Decision: tweak",
                        "Selected strategy: 密集研究工作台",
                        "Evidence kind: pasted_summary",
                        "Prompt intent: targeted_modification",
                        "Brief revision:",
                        "",
                        review["findings"][0]["issue"],
                        review["findings"][0]["recommended_change"],
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            for target in ["huashu-design", "claude-design", "v0"]:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(EXPORT_MODIFICATION),
                        "--review",
                        "reviews/result-review-pasted-summary.json",
                        "--brief",
                        "design-brief.json",
                        "--design",
                        "DESIGN.md",
                        "--target",
                        target,
                        "--out",
                        f"prompts/{target}-modification.txt",
                    ],
                    cwd=copied,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_review_demo.py"), str(copied)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review guidance is not Chinese-first", result.stdout + result.stderr)

    def test_validate_comparison_demo(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATE_COMPARISON), str(COMPARISON_DIR)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("valid", result.stdout.lower())

    def test_validate_comparison_demo_rejects_misleading_or_incomplete_package(self):
        def update_manifest(demo, transform):
            path = demo / "comparison-demo.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            transform(payload)
            path.write_text(json.dumps(payload), encoding="utf-8")

        def make_manifest_paths_absolute(root, demo):
            def transform(payload):
                payload["enhanced"]["source_path"] = str((root / "examples" / "ai-search-landing").resolve())
                payload["page"]["path"] = str((demo / "index.html").resolve())
                payload["future_real_output_todo_path"] = str((demo / "future-real-output-todo.md").resolve())

            update_manifest(demo, transform)

        cases = [
            (
                "missing_disclosure",
                lambda root, demo: (demo / "index.html").write_text(
                    (demo / "index.html").read_text(encoding="utf-8").replace(
                        "不是命名工具输出",
                        "工具输出",
                    ),
                    encoding="utf-8",
                ),
                "index.html missing required text",
            ),
            (
                "english_html_language",
                lambda root, demo: (demo / "index.html").write_text(
                    (demo / "index.html").read_text(encoding="utf-8").replace(
                        'lang="zh-CN"',
                        'lang="en"',
                    ),
                    encoding="utf-8",
                ),
                'index.html html lang must be "zh-CN"',
            ),
            (
                "missing_future_todo",
                lambda root, demo: (demo / "future-real-output-todo.md").unlink(),
                "missing required file: future-real-output-todo.md",
            ),
            (
                "invalid_enhanced_path",
                lambda root, demo: update_manifest(demo, lambda payload: payload["enhanced"].update({"source_path": "examples/missing"})),
                "enhanced.source_path does not resolve",
            ),
            (
                "absolute_manifest_path",
                make_manifest_paths_absolute,
                "must be repo-relative",
            ),
            (
                "named_tool_baseline_claim",
                lambda root, demo: update_manifest(
                    demo,
                    lambda payload: payload["baseline"].update({"source_type": "v0", "summary": "Actual v0 output."}),
                ),
                "baseline must not claim a named-tool source",
            ),
            (
                "missing_visual_marker",
                lambda root, demo: (demo / "index.html").write_text(
                    (demo / "index.html").read_text(encoding="utf-8").replace(
                        'data-demo-region="baseline-mockup"',
                        'data-demo-region="baseline-copy"',
                    ),
                    encoding="utf-8",
                ),
                "index.html missing visual mockup marker",
            ),
            (
                "remote_dependency",
                lambda root, demo: (demo / "index.html").write_text(
                    (demo / "index.html").read_text(encoding="utf-8").replace(
                        "</head>",
                        '<script src="https://example.test/app.js"></script></head>',
                    ),
                    encoding="utf-8",
                ),
                "remote asset",
            ),
            (
                "missing_readme_link",
                lambda root, demo: (root / "README.md").write_text("# BriefPilot\n", encoding="utf-8"),
                "README.md must link",
            ),
            (
                "plain_readme_path",
                lambda root, demo: (root / "README.md").write_text(
                    "# BriefPilot\n\nOpen examples/comparison-demo/index.html.\n",
                    encoding="utf-8",
                ),
                "README.md must link",
            ),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            for name, mutate, expected in cases:
                root = Path(tmp) / name
                demo = write_comparison_demo(root)
                mutate(root, demo)
                result = run_comparison_validator(root, demo)
                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn("invalid comparison demo", result.stdout)
                self.assertIn(expected, result.stdout + result.stderr)

    def test_export_all_prompt_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            for target in ["huashu-design", "claude-design", "v0"]:
                out = Path(tmp) / f"{target}.txt"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "export_prompt.py"),
                        "--brief",
                        str(EXAMPLE),
                        "--design",
                        str(DESIGN_MD),
                        "--target",
                        target,
                        "--out",
                        str(out),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                text = out.read_text(encoding="utf-8")
                self.assertIn("Task", text)
                self.assertIn("Output Language", text)
                self.assertIn("用户可见 UI 文案必须使用简体中文", text)
                self.assertIn("Use Simplified Chinese for all user-visible UI copy.", text)
                self.assertIn("Visual Strategy", text)
                self.assertIn("DESIGN.md Visual System", text)
                self.assertIn("Review Criteria", text)
                self.assertIn("企业信任型", text)
                self.assertIn("搜索助手演示型", text)
                self.assertIn("创始人发布型", text)
                self.assertIn("Interaction contract", text)
                self.assertIn("Responsive and accessibility requirements", text)
                self.assertIn("移动端触控目标至少 44px", text)

    def test_result_review_references_are_linked(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "result-review-workflow.md").read_text(encoding="utf-8")
        visual = (ROOT / "references" / "visual-review-routing.md").read_text(encoding="utf-8")
        asset_layout = (ROOT / "references" / "asset-layout.md").read_text(encoding="utf-8")

        self.assertIn("references/result-review-workflow.md", skill)
        self.assertIn("references/visual-review-routing.md", skill)
        for decision in ["accept", "tweak", "revise_brief_then_regenerate", "regenerate_from_scratch"]:
            self.assertIn(decision, workflow)
        self.assertIn("pasted_summary", workflow)
        self.assertIn("local_file", workflow)
        self.assertIn("does not actively open pages", workflow)
        self.assertIn("available_gstack", visual)
        self.assertIn("not block text or file review", visual)
        self.assertIn("reviews/result-review.json", asset_layout)
        self.assertIn("prompts/<target>-modification.txt", asset_layout)

    def test_docs_describe_design_md_checks_without_silent_install(self):
        readme = ROOT.joinpath("README.md").read_text(encoding="utf-8")
        design_doc = (ROOT / "references" / "design-md.md").read_text(encoding="utf-8")
        asset_layout = (ROOT / "references" / "asset-layout.md").read_text(encoding="utf-8")
        combined = "\n".join([readme, design_doc, asset_layout])
        self.assertIn("Google-style DESIGN.md", readme)
        self.assertIn("built-in", combined.lower())
        self.assertIn("optional", combined.lower())
        self.assertIn("never silently installs npm packages", readme)
        self.assertIn("never automatically runs `npx`", readme)
        self.assertIn("reviews/design-md-review.md", asset_layout)
        self.assertIn("reviews/design-md-review.json", asset_layout)

    def test_public_package_has_no_private_or_old_wrapper_paths(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATE_PUBLIC_PACKAGE)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_public_package_validator_allows_ignored_local_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            (root / "AGENTS.md").write_text("local rules\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "note.md").write_text("local note\n", encoding="utf-8")

            result = run_public_package_validator(root)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_public_package_validator_rejects_tracked_local_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "note.md").write_text("local note\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "-f", "docs/note.md"],
                text=True,
                capture_output=True,
                check=True,
            )

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("local-only path is tracked", result.stdout)

    def test_public_package_validator_rejects_tracked_root_agent_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            (root / "AGENTS.md").write_text("local rules\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "-f", "AGENTS.md"],
                text=True,
                capture_output=True,
                check=True,
            )

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("local-only path is tracked", result.stdout)

    def test_public_package_validator_rejects_unignored_local_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp, gitignore="/AGENTS.md\n/需求文档/\n")
            (root / "docs").mkdir()
            (root / "docs" / "note.md").write_text("local note\n", encoding="utf-8")

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("local-only path is not ignored by git: docs", result.stdout)
            self.assertIn("local-only path is untracked but not ignored", result.stdout)

    def test_public_package_validator_rejects_old_wrapper_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            (root / "briefpilot").mkdir()
            (root / "briefpilot" / "SKILL.md").write_text("# Old wrapper\n", encoding="utf-8")

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden top-level workspace path exists: briefpilot", result.stdout)

    def test_public_package_validator_rejects_old_source_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            (root / "需求文档").mkdir()
            (root / "需求文档" / "note.md").write_text("old source\n", encoding="utf-8")

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden top-level workspace path exists: 需求文档", result.stdout)

    def test_public_package_validator_rejects_private_source_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            marker = "ClaudeDesign_" + "泄露" + "提示词.md"
            (root / "README.md").write_text(f"# BriefPilot\n\n{marker}\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "README.md"],
                text=True,
                capture_output=True,
                check=True,
            )

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("private source material marker", result.stdout)

    def test_public_package_validator_rejects_local_home_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            local_path = "/" + "Users/example/Desktop/" + "project/BriefPilot"
            (root / "README.md").write_text(f"# BriefPilot\n\n{local_path}\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "README.md"],
                text=True,
                capture_output=True,
                check=True,
            )

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contains forbidden local text", result.stdout)

    def test_public_package_validator_rejects_old_wrapper_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = init_public_package_repo(tmp)
            old_path = "brief" + "pilot/scripts/export_prompt.py"
            (root / "README.md").write_text(f"# BriefPilot\n\n{old_path}\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "README.md"],
                text=True,
                capture_output=True,
                check=True,
            )

            result = run_public_package_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("old wrapper path", result.stdout)

    def test_result_review_templates_define_contract(self):
        review_template = json.loads((ROOT / "templates" / "result-review.json").read_text(encoding="utf-8"))
        prompt_template = (ROOT / "templates" / "modification-prompt.txt").read_text(encoding="utf-8")
        revision_template = (ROOT / "templates" / "brief-revision.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "result-review-workflow.md").read_text(encoding="utf-8")

        for field in ["schema_version", "source", "target_tool", "evidence", "decision", "selected_strategy", "strategy_preserved", "findings", "visual_review", "prompt"]:
            self.assertIn(field, review_template)
        for value in ["pasted_summary", "local_file", "screenshot_reference", "gstack_report"]:
            self.assertIn(value, workflow)
        for value in ["targeted_modification", "brief_revision_regeneration", "full_regeneration"]:
            self.assertIn(value, workflow)
        self.assertIn("DESIGN.md Visual Rules To Preserve", prompt_template)
        self.assertIn("用户可见 UI 文案必须使用简体中文", prompt_template)
        self.assertIn("Use Simplified Chinese for all user-visible UI copy.", prompt_template)
        self.assertIn("Source Brief Context", prompt_template)
        self.assertIn("What To Keep", prompt_template)
        self.assertIn("What To Change", prompt_template)
        self.assertIn("What Not To Change", prompt_template)
        self.assertIn("除非已经实际保存更新后的 brief 文件，否则不要暗示完整 brief 已经被重写", revision_template)

    def test_validate_pasted_summary_review_and_export_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = write_review_package(tmp)
            review_path = write_review(package / "review.json", base_review())
            result = subprocess.run(
                [sys.executable, str(VALIDATE_REVIEW), str(review_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            out = package / "prompt.txt"
            result = subprocess.run(
                [
                    sys.executable,
                    str(EXPORT_MODIFICATION),
                    "--review",
                    str(review_path),
                    "--brief",
                    "design-brief.json",
                    "--design",
                    "DESIGN.md",
                    "--target",
                    "v0",
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            text = out.read_text(encoding="utf-8")
            self.assertIn("Dense Research Workspace", text)
            self.assertIn("用户可见 UI 文案必须使用简体中文", text)
            self.assertIn("Use Simplified Chinese for all user-visible UI copy.", text)
            self.assertIn("Source Brief Context", text)
            self.assertIn("Primary user: research teams", text)
            self.assertIn("Business goal: increase answer trust", text)
            self.assertIn("Review Criteria", text)
            self.assertIn("DESIGN.md Visual Rules To Preserve", text)
            self.assertIn("restrained blue accents", text)
            self.assertIn("Make source cards visible", text)

    def test_validate_brief_revision_accept_and_full_regeneration_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = write_review_package(tmp)
            revision = base_review(
                evidence={
                    "kind": "local_file",
                    "summary": "The local result lacks source disagreement handling.",
                    "path": "generated.html",
                },
                decision="revise_brief_then_regenerate",
                brief_revision_path="brief-revision.md",
                prompt_intent="brief_revision_regeneration",
                prompt={
                    "keep": ["Keep dense answer and source layout."],
                    "change": ["Add source disagreement and expired-source recovery guidance."],
                    "do_not_change": ["Do not change the visual system."],
                    "acceptance_checks": ["Conflicting sources have a visible explanation path."],
                },
                visual_review={"status": "not_provided", "notes": "No visual evidence was supplied."},
            )
            revision_path = write_review(package / "revision.json", revision)
            result = subprocess.run(
                [sys.executable, str(VALIDATE_REVIEW), str(revision_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            accept = base_review(
                decision="accept",
                findings=[],
                visual_review={"status": "not_provided", "notes": "No visual evidence was supplied."},
            )
            accept.pop("prompt_intent")
            accept.pop("prompt")
            accept_path = write_review(package / "accept.json", accept)
            result = subprocess.run(
                [sys.executable, str(VALIDATE_REVIEW), str(accept_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            regenerate = base_review(
                decision="regenerate_from_scratch",
                selected_strategy="Evidence-First Reset",
                strategy_preserved=False,
                strategy_change_reason="The generated result ignored the app-page structure and needs a stricter evidence-first direction.",
                prompt_intent="full_regeneration",
                prompt={
                    "keep": ["Keep the same audience and answer trust goal."],
                    "change": ["Regenerate around evidence-first answer review."],
                    "do_not_change": ["Do not invent unsupported customer proof."],
                    "acceptance_checks": ["The first screen shows query, confidence, answer, and source origin."],
                },
                visual_review={"status": "not_provided", "notes": "No visual evidence was supplied."},
            )
            regenerate_path = write_review(package / "regenerate.json", regenerate)
            out = package / "regenerate-prompt.txt"
            result = subprocess.run(
                [
                    sys.executable,
                    str(EXPORT_MODIFICATION),
                    "--review",
                    str(regenerate_path),
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            text = out.read_text(encoding="utf-8")
            self.assertIn("Regenerate the result from scratch", text)
            self.assertIn("Evidence-First Reset", text)
            self.assertIn("Strategy may change only for this reason", text)
            self.assertIn("Primary user: research teams", text)

    def test_validate_result_review_rejects_invalid_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = write_review_package(tmp)
            missing_strategy_brief = json.loads((package / "design-brief.json").read_text(encoding="utf-8"))
            missing_strategy_brief.pop("visual")
            missing_strategy_brief["strategy_options"] = [{"name": "Dense Research Workspace", "selected": False}]
            (package / "brief-without-strategy.json").write_text(json.dumps(missing_strategy_brief), encoding="utf-8")
            (package / "array-brief.json").write_text("[]", encoding="utf-8")
            (package / "bad-encoding.md").write_bytes(b"\xff")

            cases = [
                ("bad_decision.json", base_review(decision="polish"), "decision must be one of"),
                ("missing_local_path.json", base_review(evidence={"kind": "local_file", "summary": "Missing path."}), "evidence.path is required"),
                ("empty_local_file.json", base_review(evidence={"kind": "local_file", "summary": "Empty file.", "path": "empty.md"}), "non-whitespace content"),
                ("bad_local_suffix.json", base_review(evidence={"kind": "local_file", "summary": "Bad suffix.", "path": "generated.png"}), "unsupported suffix"),
                ("bad_encoding_local_file.json", base_review(evidence={"kind": "local_file", "summary": "Bad encoding.", "path": "bad-encoding.md"}), "readable UTF-8 text"),
                ("design_mismatch.json", base_review(source={"brief_path": "design-brief.json", "design_md_path": "other-DESIGN.md"}), "source.design_md_path must match"),
                (
                    "visual_conflict.json",
                    base_review(
                    evidence={"kind": "gstack_report", "summary": "Report text.", "path": "report.md"},
                    visual_review={"status": "unavailable", "notes": "Fallback."},
                ),
                    "available_gstack",
                ),
                ("prompt_mismatch.json", base_review(prompt_intent="full_regeneration"), "prompt_intent must be targeted_modification"),
                ("blank_prompt_item.json", base_review(prompt={"keep": ["   "], "change": ["Make source cards visible."], "acceptance_checks": ["Source cards are visible."]}), "prompt.keep[0] must be non-empty text"),
                ("missing_findings.json", base_review(findings=[]), "findings must be a non-empty array"),
                ("strategy_mismatch.json", base_review(selected_strategy="Other Strategy"), "selected_strategy must match"),
                (
                    "missing_source_strategy.json",
                    base_review(source={"brief_path": "brief-without-strategy.json", "design_md_path": "DESIGN.md"}),
                    "source brief must define selected strategy",
                ),
                ("array_source_brief.json", base_review(source={"brief_path": "array-brief.json", "design_md_path": "DESIGN.md"}), "source.brief_path must be a JSON object"),
            ]
            for filename, review, expected in cases:
                review_path = write_review(package / filename, review)
                result = subprocess.run(
                    [sys.executable, str(VALIDATE_REVIEW), str(review_path)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0, filename)
                self.assertIn("invalid result review", result.stdout)
                self.assertIn(expected, result.stdout + result.stderr)

            non_object_review = package / "array-review.json"
            non_object_review.write_text("[]", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATE_REVIEW), str(non_object_review)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review must be a JSON object", result.stdout + result.stderr)

    def test_validate_review_demo_catches_markdown_json_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "ai-search-workspace"
            shutil.copytree(WORKSPACE_DIR, copied)
            markdown = copied / "reviews" / "result-review-pasted-summary.md"
            text = markdown.read_text(encoding="utf-8").replace("Decision: tweak", "Decision: accept")
            markdown.write_text(text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_review_demo.py"), str(copied)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("markdown decision does not match JSON", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
