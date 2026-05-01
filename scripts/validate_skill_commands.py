#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import validate_release_metadata


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ("briefpilot", "bp", "bp-review", "briefpilot-upgrade")
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
COMPANION_ALLOWED_PARTS = {
    ("SKILL.md",),
    ("agents", "openai.yaml"),
    ("evals", "evals.json"),
    ("install-manifest.json",),
}
FORBIDDEN_PACKAGE_PARTS = {
    "AGENTS.md",
    "docs",
    ".git",
    "__pycache__",
    "evals",
    "companions",
    "briefpilot-skill-workspace",
    "dist",
}


def has_cjk(text):
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def read_text(path, findings, label):
    path = Path(path)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        findings.append(f"missing {label}: {path}")
    except UnicodeDecodeError:
        findings.append(f"{path} is not readable UTF-8")
    except OSError as error:
        findings.append(f"{path} is not readable: {error}")
    return None


def parse_frontmatter(path, findings):
    text = read_text(path, findings, "SKILL.md")
    if text is None:
        return None, ""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        findings.append(f"{path} missing YAML frontmatter")
        return None, text

    frontmatter = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            findings.append(f"{path} has unsupported frontmatter line: {raw_line}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        frontmatter[key] = value

    unexpected = set(frontmatter) - ALLOWED_FRONTMATTER
    if unexpected:
        findings.append(f"{path} has unexpected frontmatter keys: {', '.join(sorted(unexpected))}")

    return frontmatter, text


def validate_skill_file(path, expected_name, required_terms, findings):
    frontmatter, text = parse_frontmatter(path, findings)
    if frontmatter is None:
        return

    name = frontmatter.get("name")
    description = frontmatter.get("description", "")
    if name != expected_name:
        findings.append(f"{path} name must be {expected_name}, got {name!r}")
    if not isinstance(name, str) or not re.match(r"^[a-z0-9-]+$", name or ""):
        findings.append(f"{path} name must use lowercase letters, digits, and hyphens")
    if name and (name.startswith("-") or name.endswith("-") or "--" in name):
        findings.append(f"{path} name cannot start/end with hyphen or contain consecutive hyphens")
    if name and len(name) > MAX_NAME_LENGTH:
        findings.append(f"{path} name is longer than {MAX_NAME_LENGTH} characters")
    if not description:
        findings.append(f"{path} description is required")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        findings.append(f"{path} description is longer than {MAX_DESCRIPTION_LENGTH} characters")
    if "<" in description or ">" in description:
        findings.append(f"{path} description cannot contain angle brackets")

    missing_terms = [term for term in required_terms if term not in description and term not in text]
    if missing_terms:
        findings.append(f"{path} missing command or routing terms: {', '.join(missing_terms)}")


def load_json(path, findings):
    text = read_text(path, findings, "JSON file")
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        findings.append(f"{path} is not valid JSON: {error}")
        return None


def validate_evals(path, expected_skill, min_count, findings):
    payload = load_json(path, findings)
    if not isinstance(payload, dict):
        return
    if payload.get("skill_name") != expected_skill:
        findings.append(f"{path} skill_name must be {expected_skill}")
    evals = payload.get("evals")
    if not isinstance(evals, list) or len(evals) < min_count:
        findings.append(f"{path} must contain at least {min_count} evals")
        return

    ids = set()
    for index, item in enumerate(evals, start=1):
        if not isinstance(item, dict):
            findings.append(f"{path} eval {index} must be an object")
            continue
        eval_id = item.get("id")
        if not isinstance(eval_id, int) or eval_id in ids:
            findings.append(f"{path} eval {index} has missing or duplicate integer id")
        ids.add(eval_id)
        prompt = item.get("prompt", "")
        expected_output = item.get("expected_output", "")
        expectations = item.get("expectations", [])
        if not isinstance(prompt, str) or len(prompt.strip()) < 20:
            findings.append(f"{path} eval {index} prompt is too short to exercise a skill")
        if not has_cjk(prompt):
            findings.append(f"{path} eval {index} prompt must include Chinese user-facing text")
        if not isinstance(expected_output, str) or len(expected_output.strip()) < 30:
            findings.append(f"{path} eval {index} expected_output is too thin")
        if not isinstance(expectations, list) or len(expectations) < 3:
            findings.append(f"{path} eval {index} must include at least 3 expectations")
        for expectation in expectations:
            if not isinstance(expectation, str) or len(expectation.strip()) < 20:
                findings.append(f"{path} eval {index} has a weak expectation")


def validate_companion_is_lean(companion_dir, findings):
    for path in companion_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(companion_dir)
        if relative.parts not in COMPANION_ALLOWED_PARTS:
            findings.append(f"{companion_dir} contains non-lean companion file: {relative.as_posix()}")

    for forbidden in ("references", "templates", "scripts", "examples"):
        if (companion_dir / forbidden).exists():
            findings.append(f"{companion_dir} must not duplicate main {forbidden}/ resources")


def validate_briefpilot_flow_terms(root, findings):
    skill_text = read_text(root / "SKILL.md", findings, "SKILL.md") or ""
    readme_text = read_text(root / "README.md", findings, "README.md") if (root / "README.md").exists() else ""
    readme_text = readme_text or ""
    eval_text = json.dumps(load_json(root / "evals" / "evals.json", findings) or {}, ensure_ascii=False)
    bp_eval_text = json.dumps(load_json(root / "companions" / "bp" / "evals" / "evals.json", findings) or {}, ensure_ascii=False)
    bp_review_eval_text = json.dumps(
        load_json(root / "companions" / "bp-review" / "evals" / "evals.json", findings) or {},
        ensure_ascii=False,
    )
    combined = "\n".join([skill_text, readme_text, eval_text, bp_eval_text, bp_review_eval_text])
    for term in ["START_HERE.md", "design-spec.md", "review-next-actions.md"]:
        if term not in combined:
            findings.append(f"command workflow docs/evals missing new flow term: {term}")
    if "可选" not in combined or "optional" not in combined.lower():
        findings.append("command workflow docs/evals must describe platform prompts as optional exports")
    if "generic" not in skill_text or "首轮平台提示词" not in skill_text:
        findings.append("SKILL.md must state generic is not a first-run prompt target")
    if "不改" not in combined and "does not edit" not in combined:
        findings.append("command workflow docs/evals must enforce review-only safety")


def validate_source(root):
    root = Path(root).resolve()
    findings = []
    findings.extend(validate_release_metadata.validate(root))
    validate_skill_file(root / "SKILL.md", "briefpilot", ["/briefpilot", "DESIGN.md"], findings)
    validate_skill_file(root / "companions" / "bp" / "SKILL.md", "bp", ["/bp", "briefpilot"], findings)
    validate_skill_file(
        root / "companions" / "bp-review" / "SKILL.md",
        "bp-review",
        ["/bp-review", "briefpilot", "result-review"],
        findings,
    )
    validate_skill_file(
        root / "companions" / "briefpilot-upgrade" / "SKILL.md",
        "briefpilot-upgrade",
        ["/briefpilot-upgrade", ".skill"],
        findings,
    )

    validate_evals(root / "evals" / "evals.json", "briefpilot", 3, findings)
    validate_evals(root / "companions" / "bp" / "evals" / "evals.json", "bp", 2, findings)
    validate_evals(
        root / "companions" / "bp-review" / "evals" / "evals.json",
        "bp-review",
        2,
        findings,
    )
    validate_evals(
        root / "companions" / "briefpilot-upgrade" / "evals" / "evals.json",
        "briefpilot-upgrade",
        2,
        findings,
    )

    validate_companion_is_lean(root / "companions" / "bp", findings)
    validate_companion_is_lean(root / "companions" / "bp-review", findings)
    validate_companion_is_lean(root / "companions" / "briefpilot-upgrade", findings)
    validate_briefpilot_flow_terms(root, findings)

    for required in [
        "scripts/package_briefpilot_skills.py",
        "scripts/validate_release_metadata.py",
        "scripts/validate_skill_commands.py",
    ]:
        if not (root / required).exists():
            findings.append(f"missing command package script: {required}")

    gitignore = root / ".gitignore"
    text = read_text(gitignore, findings, ".gitignore")
    if text is not None:
        for pattern in ["/dist/", "/briefpilot-skill-workspace/"]:
            if pattern not in text:
                findings.append(f".gitignore missing generated artifact ignore: {pattern}")

    return findings


def load_install_manifest(skill_dir, findings):
    path = Path(skill_dir) / "install-manifest.json"
    if not path.exists():
        findings.append(f"installed command missing install manifest: {Path(skill_dir).name}")
        return None
    return validate_release_metadata.load_manifest(path, findings)


def validate_installed(install_dir, expected_version=None, expected_source_commit=None):
    install_dir = Path(install_dir).resolve()
    findings = []
    manifests = {}
    for command in COMMANDS:
        skill_dir = install_dir / command
        if not skill_dir.is_dir():
            findings.append(f"installed command missing: {command}")
            continue
        validate_skill_file(skill_dir / "SKILL.md", command, [command], findings)
        manifest = load_install_manifest(skill_dir, findings)
        if manifest is not None:
            manifests[command] = manifest

    main_dir = install_dir / "briefpilot"
    if main_dir.exists():
        for part in FORBIDDEN_PACKAGE_PARTS:
            if (main_dir / part).exists():
                findings.append(f"installed briefpilot contains forbidden package part: {part}")
        for required in ["SKILL.md", "VERSION", "CHANGELOG.md", "references", "templates", "scripts", "examples"]:
            if not (main_dir / required).exists():
                findings.append(f"installed briefpilot missing required part: {required}")
        release_findings = validate_release_metadata.validate(main_dir)
        findings.extend(f"installed briefpilot {finding}" for finding in release_findings)
        if expected_version and (main_dir / "VERSION").exists():
            try:
                installed_version = validate_release_metadata.read_version(main_dir)
                if installed_version != expected_version:
                    findings.append(
                        f"installed briefpilot VERSION {installed_version!r} differs from root VERSION {expected_version!r}"
                    )
            except (OSError, UnicodeDecodeError) as error:
                findings.append(f"installed briefpilot VERSION is not readable: {error}")

    for command in ("bp", "bp-review", "briefpilot-upgrade"):
        skill_dir = install_dir / command
        if skill_dir.exists():
            validate_companion_is_lean(skill_dir, findings)

    manifest_expected_version = expected_version
    if manifest_expected_version is None and (main_dir / "VERSION").exists():
        try:
            manifest_expected_version = validate_release_metadata.read_version(main_dir)
        except (OSError, UnicodeDecodeError):
            manifest_expected_version = None
    if manifests:
        validate_release_metadata.validate_manifest_set(
            manifests,
            manifest_expected_version,
            findings,
            expected_source_commit=expected_source_commit,
        )

    return findings


def git_commit(root):
    root = Path(root).resolve()
    top_level = git_root(root)
    if top_level != root:
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    commit = result.stdout.strip()
    return commit if re.fullmatch(r"[0-9a-f]{40}", commit) else None


def git_root(root):
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return Path(value).resolve() if value else None


def git_commit_exists(root, commit):
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def validate_archive_member_names(archive_name, command, names):
    findings = []
    for name in names:
        if not name or name.endswith("/"):
            continue
        if name.startswith("/"):
            findings.append(f"{archive_name} contains unsafe absolute path: {name}")
            continue
        parts = PurePosixPath(name).parts
        if not parts or parts[0] != command:
            findings.append(f"{archive_name} contains unexpected path: {name}")
            continue
        if any(part in {"", ".", ".."} for part in parts):
            findings.append(f"{archive_name} contains unsafe relative path: {name}")
    return findings


def validate_dist(dist_dir, source_root=DEFAULT_ROOT):
    dist_dir = Path(dist_dir).resolve()
    findings = []
    expected_version = None
    expected_source_commit = None
    if source_root is not None:
        source_root = Path(source_root).resolve()
        try:
            expected_version = validate_release_metadata.read_version(source_root)
        except (OSError, UnicodeDecodeError):
            expected_version = None
        source_git_root = git_root(source_root)
        if source_git_root is None:
            findings.append("source git commit is unavailable; dist source_commit cannot be verified")
        elif source_git_root != source_root:
            findings.append(f"source root must be the git repository root: {source_root}")
        expected_source_commit = git_commit(source_root)
        if expected_source_commit and not git_commit_exists(source_root, expected_source_commit):
            findings.append(f"source commit does not exist locally: {expected_source_commit}")
            expected_source_commit = None
    with tempfile.TemporaryDirectory(prefix="briefpilot-skill-validate-") as tmp:
        extracted_root = Path(tmp)
        can_validate_installed = True
        for command in COMMANDS:
            archive = dist_dir / f"{command}.skill"
            if not archive.exists():
                findings.append(f"missing package artifact: {archive.name}")
                can_validate_installed = False
                continue
            try:
                with zipfile.ZipFile(archive) as zip_file:
                    names = zip_file.namelist()
                    path_findings = validate_archive_member_names(archive.name, command, names)
                    if path_findings:
                        findings.extend(path_findings)
                        can_validate_installed = False
                        continue
                    if not any(name == f"{command}/SKILL.md" for name in names):
                        findings.append(f"{archive.name} must contain {command}/SKILL.md")
                        can_validate_installed = False
                    wrong_roots = {name.split("/", 1)[0] for name in names if name and not name.startswith(f"{command}/")}
                    if wrong_roots:
                        findings.append(f"{archive.name} contains unexpected top-level roots: {', '.join(sorted(wrong_roots))}")
                        can_validate_installed = False
                    forbidden_hits = []
                    for name in names:
                        parts = PurePosixPath(name).parts
                        if any(part in FORBIDDEN_PACKAGE_PARTS for part in parts[1:]):
                            forbidden_hits.append(name)
                    if forbidden_hits:
                        findings.append(f"{archive.name} contains forbidden package paths: {', '.join(forbidden_hits[:5])}")
                        can_validate_installed = False
                    if can_validate_installed:
                        zip_file.extractall(extracted_root)
            except zipfile.BadZipFile:
                findings.append(f"{archive.name} is not a valid zip archive")
                can_validate_installed = False
                continue
        if can_validate_installed:
            findings.extend(
                validate_installed(
                    extracted_root,
                    expected_version=expected_version,
                    expected_source_commit=expected_source_commit,
                )
            )
    return findings


def emit_json(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def result_payload(args, root, findings):
    ok = not findings
    message = "valid BriefPilot command package" if ok else "invalid BriefPilot command package"
    return {
        "ok": ok,
        "kind": "validate_skill_commands",
        "root": str(Path(root).resolve()) if root else None,
        "installed_dir": str(Path(args.installed_dir).resolve()) if args.installed_dir else None,
        "dist_dir": str(Path(args.dist_dir).resolve()) if args.dist_dir else None,
        "findings": findings,
        "message": message,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Validate BriefPilot command Skill packaging.")
    parser.add_argument("--root", type=Path, help="Repository root to validate.")
    parser.add_argument("--installed-dir", type=Path, help="Validate an installed skills directory.")
    parser.add_argument("--dist-dir", type=Path, help="Validate generated .skill artifacts.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="Output format. Defaults to text.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve() if args.root else DEFAULT_ROOT
    validate_source_root = args.root is not None or args.dist_dir or not args.installed_dir
    findings = validate_source(root) if validate_source_root else []
    if args.installed_dir:
        expected_version = None
        if validate_source_root:
            try:
                expected_version = validate_release_metadata.read_version(root)
            except (OSError, UnicodeDecodeError):
                expected_version = None
        findings.extend(validate_installed(args.installed_dir, expected_version=expected_version))
    if args.dist_dir:
        findings.extend(validate_dist(args.dist_dir, root))

    payload = result_payload(args, root if validate_source_root or args.root else None, findings)
    if args.output_format == "json":
        emit_json(payload)
        return 0 if payload["ok"] else 1

    if findings:
        print("invalid BriefPilot command package:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("valid BriefPilot command package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
