#!/usr/bin/env python3
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_TOP_LEVEL_FILES = {".gitignore", "LICENSE", "README.md", "SKILL.md"}
ALLOWED_TOP_LEVEL_DIRS = {"agents", "examples", "references", "scripts", "templates"}
FORBIDDEN_TOP_LEVEL = {"AGENTS.md", "briefpilot", "docs", "需求文档"}
FORBIDDEN_TEXT = [
    "/" + "Users/",
    "Desktop/" + "project",
    "kang" + "jiaqi",
]
OLD_WRAPPER_RE = re.compile(r"(?<!\.)" + "briefpilot" + r"/")
SKIP_DIRS = {".git", "__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def should_skip(path):
    parts = set(path.parts)
    return (
        bool(parts & SKIP_DIRS)
        or path.suffix in SKIP_SUFFIXES
        or any(part.startswith(".") and part != ".gitignore" for part in path.parts)
    )


def iter_public_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not should_skip(path.relative_to(ROOT)):
            yield path


def main():
    findings = []

    for name in sorted(FORBIDDEN_TOP_LEVEL):
        if (ROOT / name).exists():
            findings.append(f"forbidden top-level entry exists: {name}")

    for entry in sorted(ROOT.iterdir(), key=lambda path: path.name):
        if entry.name.startswith(".") and entry.name != ".gitignore":
            continue
        if entry.is_dir() and entry.name not in ALLOWED_TOP_LEVEL_DIRS:
            findings.append(f"unexpected top-level directory: {entry.name}")
        elif entry.is_file() and entry.name not in ALLOWED_TOP_LEVEL_FILES:
            findings.append(f"unexpected top-level file: {entry.name}")

    readme = ROOT / "README.md"
    if readme.exists():
        readme_text = readme.read_text(encoding="utf-8")
        old_scripts_path = "briefpilot" + "/scripts/"
        old_skill_path = "briefpilot" + "/SKILL.md"
        if old_scripts_path in readme_text or old_skill_path in readme_text:
            findings.append("README.md still uses old wrapper command paths")

    for path in iter_public_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-UTF-8 text file: {path.relative_to(ROOT)}")
            continue
        relative = path.relative_to(ROOT)
        for token in FORBIDDEN_TEXT:
            if token in text:
                findings.append(f"{relative} contains forbidden local text: {token}")
        if OLD_WRAPPER_RE.search(text):
            findings.append(f"{relative} contains old wrapper path")

    if findings:
        print("invalid public package:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"valid public package: {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
