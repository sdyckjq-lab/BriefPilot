#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
CHANGELOG_ENTRY_PATTERN = re.compile(r"^## \[(\d+\.\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})\s*$")
ALLOWED_CHANGELOG_SECTIONS = {"Added", "Changed", "Fixed", "Removed"}
COMMANDS = ("briefpilot", "bp", "briefpilot-upgrade")
OFFICIAL_SOURCE_REMOTE = "https://github.com/sdyckjq-lab/BriefPilot.git"


def parse_version(value):
    if not isinstance(value, str):
        raise ValueError("version must be a string")
    value = value.strip()
    if not VERSION_PATTERN.fullmatch(value):
        raise ValueError("version must use MAJOR.MINOR.PATCH.MICRO")
    return tuple(int(part) for part in value.split("."))


def compare_versions(left, right):
    left_parts = parse_version(left)
    right_parts = parse_version(right)
    if left_parts == right_parts:
        return 0
    return 1 if left_parts > right_parts else -1


def read_version(root):
    return (Path(root) / "VERSION").read_text(encoding="utf-8").strip()


def validate_version_file(root, findings):
    path = Path(root) / "VERSION"
    if not path.exists():
        findings.append("missing VERSION")
        return None

    raw = path.read_text(encoding="utf-8")
    value = raw.strip()
    if not value:
        findings.append("VERSION is empty")
        return None
    if raw not in {value, value + "\n"}:
        findings.append("VERSION must contain exactly one four-part version and an optional trailing newline")
    try:
        parse_version(value)
    except ValueError as error:
        findings.append(f"VERSION invalid: {error}")
        return None
    return value


def newest_changelog_entry(text):
    lines = text.splitlines()
    start = None
    match = None
    for index, line in enumerate(lines):
        match = CHANGELOG_ENTRY_PATTERN.match(line)
        if match:
            start = index
            break
    if start is None or match is None:
        return None

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return {
        "version": match.group(1),
        "date": match.group(2),
        "body": lines[start + 1 : end],
        "line": start + 1,
    }


def validate_changelog(root, expected_version, findings):
    path = Path(root) / "CHANGELOG.md"
    if not path.exists():
        findings.append("missing CHANGELOG.md")
        return

    entry = newest_changelog_entry(path.read_text(encoding="utf-8"))
    if entry is None:
        findings.append("CHANGELOG.md missing newest entry shaped as ## [X.Y.Z.W] - YYYY-MM-DD")
        return

    if expected_version and entry["version"] != expected_version:
        findings.append(
            f"CHANGELOG.md newest entry version {entry['version']} differs from VERSION {expected_version}"
        )

    try:
        datetime.strptime(entry["date"], "%Y-%m-%d")
    except ValueError:
        findings.append(f"CHANGELOG.md newest entry date is invalid: {entry['date']}")

    allowed_section_seen = False
    bullet_seen = False
    current_allowed_section = False
    for line in entry["body"]:
        stripped = line.strip()
        if stripped.startswith("### "):
            section = stripped[4:].strip()
            current_allowed_section = section in ALLOWED_CHANGELOG_SECTIONS
            if current_allowed_section:
                allowed_section_seen = True
            else:
                findings.append(f"CHANGELOG.md newest entry has unsupported section: {section}")
        elif current_allowed_section and stripped.startswith("- ") and len(stripped) > 2:
            bullet_seen = True

    if not allowed_section_seen:
        allowed = ", ".join(sorted(ALLOWED_CHANGELOG_SECTIONS))
        findings.append(f"CHANGELOG.md newest entry needs at least one allowed section: {allowed}")
    if not bullet_seen:
        findings.append("CHANGELOG.md newest entry needs at least one bullet under an allowed section")


def validate(root):
    root = Path(root).resolve()
    findings = []
    version = validate_version_file(root, findings)
    validate_changelog(root, version, findings)
    return findings


def validate_manifest_payload(payload, expected_version, findings, label="manifest"):
    if not isinstance(payload, dict):
        findings.append(f"{label} must be a JSON object")
        return

    if payload.get("schema_version") != "1.0":
        findings.append(f"{label} schema_version must be 1.0")
    if payload.get("package") != "BriefPilot":
        findings.append(f"{label} package must be BriefPilot")
    if payload.get("commands") != list(COMMANDS):
        findings.append(f"{label} commands must be {', '.join(COMMANDS)}")

    package_version = payload.get("package_version")
    if not isinstance(package_version, str):
        findings.append(f"{label} package_version is required")
    else:
        try:
            parse_version(package_version)
        except ValueError as error:
            findings.append(f"{label} package_version invalid: {error}")
        if expected_version and package_version != expected_version:
            findings.append(
                f"{label} package_version {package_version!r} differs from root VERSION {expected_version!r}"
            )

    if payload.get("source_remote") != OFFICIAL_SOURCE_REMOTE:
        findings.append(f"{label} source_remote must be {OFFICIAL_SOURCE_REMOTE}")

    source_commit = payload.get("source_commit")
    if not isinstance(source_commit, str) or not source_commit.strip():
        findings.append(f"{label} source_commit is required")

    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at.strip():
        findings.append(f"{label} generated_at is required")
    else:
        try:
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            findings.append(f"{label} generated_at must be ISO-8601")


def validate_manifest_set(manifests, expected_version, findings):
    entries = list(manifests.items()) if isinstance(manifests, dict) else list(manifests)
    for label, payload in entries:
        validate_manifest_payload(payload, expected_version, findings, label)

    for field in ("package_version", "source_remote", "source_commit"):
        values = {
            payload.get(field)
            for _label, payload in entries
            if isinstance(payload, dict) and isinstance(payload.get(field), str)
        }
        if len(values) > 1:
            findings.append(f"command manifests disagree on {field}: {', '.join(sorted(values))}")


def load_manifest(path, findings):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        findings.append(f"missing install manifest: {path}")
    except json.JSONDecodeError as error:
        findings.append(f"{path} is not valid JSON: {error}")
    return None


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate BriefPilot release metadata.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="BriefPilot repository root.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    findings = validate(args.root)
    if findings:
        print("invalid BriefPilot release metadata:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("valid BriefPilot release metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
