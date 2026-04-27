#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

ALLOWED_TOP_LEVEL_FILES = {".gitignore", "CHANGELOG.md", "LICENSE", "README.md", "SKILL.md", "VERSION"}
ALLOWED_TOP_LEVEL_DIRS = {"agents", "companions", "evals", "examples", "references", "scripts", "templates"}
LOCAL_ONLY_TOP_LEVEL = ("AGENTS.md", "docs", "需求文档")
LOCAL_ONLY_IGNORE_CHECKS = (
    ("AGENTS.md", "AGENTS.md"),
    ("docs", "docs/"),
    ("需求文档", "需求文档/"),
)
FORBIDDEN_WORKSPACE_TOP_LEVEL = ("briefpilot", "需求文档")
FORBIDDEN_TOP_LEVEL = {"AGENTS.md", "briefpilot", "docs", "需求文档"}
FORBIDDEN_TEXT = [
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
OLD_WRAPPER_RE = re.compile(r"(?<!\.)" + "briefpilot" + r"/")


def run_git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def git_lines(root, findings, *args):
    result = run_git(root, *args)
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        suffix = f": {details}" if details else ""
        findings.append(f"git {' '.join(args)} failed{suffix}")
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def tracked_paths(root, findings):
    lines = git_lines(root, findings, "ls-files")
    if lines is None:
        return None
    if not lines:
        findings.append("git ls-files returned no tracked files")
        return None
    return [Path(line) for line in lines]


def validate_tracked_public_files(root, paths, findings):
    for relative in paths:
        parts = relative.parts
        if not parts:
            continue

        top_level = parts[0]
        if top_level in FORBIDDEN_TOP_LEVEL:
            findings.append(f"forbidden tracked path: {relative.as_posix()}")
            continue

        if len(parts) == 1 and top_level not in ALLOWED_TOP_LEVEL_FILES:
            findings.append(f"unexpected tracked top-level file: {top_level}")
        elif len(parts) > 1 and top_level not in ALLOWED_TOP_LEVEL_DIRS:
            findings.append(f"unexpected tracked top-level directory: {top_level}")

        path = root / relative
        if not path.exists():
            findings.append(f"tracked path is missing from workspace: {relative.as_posix()}")
            continue
        if not path.is_file():
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-UTF-8 tracked file: {relative.as_posix()}")
            continue

        for token in FORBIDDEN_TEXT:
            if token in text:
                findings.append(f"{relative.as_posix()} contains forbidden local text: {token}")
        for token in SOURCE_MATERIAL_TEXT:
            if token in text:
                findings.append(f"{relative.as_posix()} contains private source material marker")
        if OLD_WRAPPER_RE.search(text):
            findings.append(f"{relative.as_posix()} contains old wrapper path")

    if Path("README.md") in paths:
        readme_text = (root / "README.md").read_text(encoding="utf-8")
        old_scripts_path = "briefpilot" + "/scripts/"
        old_skill_path = "briefpilot" + "/SKILL.md"
        if old_scripts_path in readme_text or old_skill_path in readme_text:
            findings.append("README.md still uses old wrapper command paths")


def validate_workspace_boundary(root, findings):
    for name in FORBIDDEN_WORKSPACE_TOP_LEVEL:
        if (root / name).exists():
            findings.append(f"forbidden top-level workspace path exists: {name}")

    for name, ignore_path in LOCAL_ONLY_IGNORE_CHECKS:
        result = run_git(root, "check-ignore", "-q", "--", ignore_path)
        if result.returncode != 0:
            findings.append(f"local-only path is not ignored by git: {name}")

    tracked = git_lines(root, findings, "ls-files", "--", *LOCAL_ONLY_TOP_LEVEL)
    if tracked:
        for path in tracked:
            findings.append(f"local-only path is tracked: {path}")

    staged = git_lines(root, findings, "diff", "--cached", "--name-only", "--", *LOCAL_ONLY_TOP_LEVEL)
    if staged:
        for path in staged:
            findings.append(f"local-only path is staged: {path}")

    status = git_lines(
        root,
        findings,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        *LOCAL_ONLY_TOP_LEVEL,
    )
    if status:
        for line in status:
            if line.startswith("??"):
                findings.append(f"local-only path is untracked but not ignored: {line[3:]}")


def validate(root):
    root = Path(root).resolve()
    findings = []
    paths = tracked_paths(root, findings)
    if paths is not None:
        validate_tracked_public_files(root, paths, findings)
    validate_workspace_boundary(root, findings)
    return findings


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate BriefPilot public package boundaries.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to validate.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    findings = validate(args.root)
    if findings:
        print("invalid public package:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("valid public package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
