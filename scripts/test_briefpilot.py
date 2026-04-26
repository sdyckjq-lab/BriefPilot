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
import validate_golden_demo


ROOT = SCRIPTS_DIR.parents[0]
EXAMPLE_DIR = ROOT / "examples" / "ai-search-landing"
EXAMPLE = EXAMPLE_DIR / "design-brief.json"
DESIGN_MD = EXAMPLE_DIR / "DESIGN.md"
WORKSPACE_DIR = ROOT / "examples" / "ai-search-workspace"
WORKSPACE_EXAMPLE = WORKSPACE_DIR / "design-brief.json"
WORKSPACE_DESIGN_MD = WORKSPACE_DIR / "DESIGN.md"
VALIDATE_REVIEW = ROOT / "scripts" / "validate_result_review.py"
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
        "meta": {"version": "0.1", "created_by": "BriefPilot", "target_tools": ["huashu-design", "claude-design", "v0"]},
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
            self.assertIn("Mode: briefpilot_fallback", markdown)
            self.assertIn("Blocking: false", markdown)
            self.assertIn("Reference direction: ai_product_landing_page", markdown)
            self.assertIn(f"- blocking: {report['summary']['blocking']}", markdown)
            self.assertIn(f"- warning: {report['summary']['warning']}", markdown)
            self.assertIn(f"- info: {report['summary']['info']}", markdown)
            self.assertIn(f"Next action: {report['next_action']}", markdown)
            self.assertIn("source_sha256", report)
            self.assertIn("Source SHA-256:", markdown)

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
                self.assertIn(f"Blocking: {str(report_payload['blocking']).lower()}", markdown)
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
            for phrase in ["Stronger token backbone", "More complete states", "Better accessibility guidance", "reference boundary"]:
                self.assertIn(phrase, proof)
            self.assertIn("prompt-readiness proof", proof)

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
                        "meta": {"version": "0.1", "created_by": "BriefPilot"},
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
                self.assertIn("Visual Strategy", text)
                self.assertIn("DESIGN.md Visual System", text)
                self.assertIn("Review Criteria", text)
                self.assertIn("Enterprise Trust", text)
                self.assertIn("Search Copilot Demo", text)
                self.assertIn("Founder-Led Launch", text)
                self.assertIn("Interaction contract", text)
                self.assertIn("Responsive and accessibility requirements", text)
                self.assertIn("44px touch target", text)

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
        self.assertIn("Source Brief Context", prompt_template)
        self.assertIn("What To Keep", prompt_template)
        self.assertIn("What To Change", prompt_template)
        self.assertIn("What Not To Change", prompt_template)
        self.assertIn("Do not imply that the full brief has been rewritten", revision_template)

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
