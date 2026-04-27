#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import validate_skill_commands
import validate_release_metadata


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ("briefpilot", "bp", "briefpilot-upgrade")
OFFICIAL_SOURCE_REMOTE = "https://github.com/sdyckjq-lab/BriefPilot.git"
MAIN_FILES = ("SKILL.md", "LICENSE", "VERSION", "CHANGELOG.md")
MAIN_DIRS = ("agents", "references", "templates", "scripts", "examples")
EXCLUDED_NAMES = {
    ".DS_Store",
    ".git",
    "__pycache__",
    "AGENTS.md",
    "docs",
    "evals",
    "companions",
    "dist",
    "briefpilot-skill-workspace",
}


def copy_filtered(src, dst):
    src = Path(src)
    dst = Path(dst)
    if src.name in EXCLUDED_NAMES:
        return
    if src.is_dir():
        def ignore(_directory, names):
            ignored = []
            for name in names:
                if name in EXCLUDED_NAMES or name.endswith(".pyc"):
                    ignored.append(name)
            return ignored

        shutil.copytree(src, dst, ignore=ignore)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def git_value(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def git_root(root):
    value = git_value(root, "rev-parse", "--show-toplevel")
    if value == "unknown":
        return None
    return Path(value).resolve()


def source_commit(root):
    value = git_value(root, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        return None
    return value


def validate_git_source(root):
    root = Path(root).resolve()
    findings = []
    top_level = git_root(root)
    if top_level is None:
        findings.append("source git commit is unavailable; commit the release source before packaging")
        return findings
    if top_level != root:
        findings.append(f"source root must be the git repository root: {root}")
    if source_commit(root) is None:
        findings.append("source git commit is unavailable; commit the release source before packaging")
    if git_dirty(root):
        findings.append("source worktree has uncommitted or untracked files; commit or ignore them before packaging")
    return findings


def git_dirty(root):
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def build_manifest(root):
    return {
        "schema_version": "1.0",
        "package": "BriefPilot",
        "commands": list(COMMANDS),
        "package_version": validate_release_metadata.read_version(root),
        "source_remote": OFFICIAL_SOURCE_REMOTE,
        "source_commit": source_commit(root) or "unknown",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def stage_main_skill(root, staging_root):
    target = staging_root / "briefpilot"
    target.mkdir(parents=True, exist_ok=True)
    for filename in MAIN_FILES:
        source = root / filename
        if source.exists():
            copy_filtered(source, target / filename)
    for dirname in MAIN_DIRS:
        source = root / dirname
        if source.exists():
            copy_filtered(source, target / dirname)
    (target / "install-manifest.json").write_text(
        json.dumps(build_manifest(root), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def stage_companion(root, staging_root, command):
    source = root / "companions" / command
    target = staging_root / command
    target.mkdir(parents=True, exist_ok=True)
    for relative in ["SKILL.md", "agents/openai.yaml"]:
        item = source / relative
        if item.exists():
            copy_filtered(item, target / relative)
    (target / "install-manifest.json").write_text(
        json.dumps(build_manifest(root), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def ensure_safe_staging_dir(root, staging_root):
    root = Path(root).resolve()
    staging_root = Path(staging_root).resolve()
    unsafe_paths = {root.parent, Path.home().resolve()}
    if staging_root == root or root in staging_root.parents:
        raise ValueError(f"refusing unsafe staging dir inside project root: {staging_root}")
    if staging_root in unsafe_paths or staging_root == staging_root.parent:
        raise ValueError(f"refusing unsafe staging dir: {staging_root}")
    if staging_root.exists():
        if not staging_root.is_dir():
            raise ValueError(f"staging dir is not a directory: {staging_root}")
        if any(staging_root.iterdir()):
            raise ValueError(f"staging dir must be empty or absent: {staging_root}")
    elif not staging_root.parent.exists():
        raise ValueError(f"staging parent does not exist: {staging_root.parent}")
    return staging_root


def stage_skills(root, staging_root):
    root = Path(root).resolve()
    staging_root = ensure_safe_staging_dir(root, staging_root)
    staging_root.mkdir(parents=True, exist_ok=True)
    stage_main_skill(root, staging_root)
    stage_companion(root, staging_root, "bp")
    stage_companion(root, staging_root, "briefpilot-upgrade")
    return staging_root


def package_skill_folder(skill_dir, out_dir):
    skill_dir = Path(skill_dir).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{skill_dir.name}.skill"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.name == ".DS_Store" or path.suffix == ".pyc":
                continue
            arcname = path.relative_to(skill_dir.parent)
            zip_file.write(path, arcname)
    return archive


def package_staged(staging_root, out_dir):
    archives = []
    for command in COMMANDS:
        archives.append(package_skill_folder(staging_root / command, out_dir))
    return archives


def can_write_install_dir(path):
    path = Path(path)
    if path.exists() and not path.is_dir():
        return False
    probe_dir = path if path.exists() else path.parent
    return probe_dir.exists() and os.access(probe_dir, os.W_OK)


def remove_path(path):
    path = Path(path)
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def valid_version_or_none(version):
    try:
        validate_release_metadata.parse_version(version)
    except ValueError:
        return None
    return version


def installed_briefpilot_versions(install_dir, findings=None):
    install_dir = Path(install_dir)
    versions = []
    version_path = install_dir / "briefpilot" / "VERSION"
    if version_path.exists():
        try:
            version = valid_version_or_none(version_path.read_text(encoding="utf-8").strip())
        except UnicodeDecodeError:
            if findings is not None:
                findings.append(f"{version_path} is not readable UTF-8")
            version = None
        except OSError as error:
            if findings is not None:
                findings.append(f"{version_path} is not readable: {error}")
            version = None
        if version:
            versions.append(version)

    for command in COMMANDS:
        manifest_path = install_dir / command / "install-manifest.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            if findings is not None:
                findings.append(f"{manifest_path} is not readable UTF-8")
            continue
        except OSError as error:
            if findings is not None:
                findings.append(f"{manifest_path} is not readable: {error}")
            continue
        except json.JSONDecodeError:
            if findings is not None:
                findings.append(f"{manifest_path} is not valid JSON")
            continue
        if not isinstance(manifest, dict):
            if findings is not None:
                findings.append(f"{manifest_path} must be a JSON object")
            continue
        version = manifest.get("package_version")
        if isinstance(version, str):
            version = valid_version_or_none(version)
            if version:
                versions.append(version)
    return versions


def highest_version(versions):
    return max(versions, key=validate_release_metadata.parse_version)


def downgrade_refusal_message(target_version, current_version):
    return (
        "refusing to install older BriefPilot version "
        f"{target_version} over installed version {current_version}; "
        "re-run with --allow-downgrade to install anyway."
    )


def downgrade_refusal_for_install(install_dir, target_version, allow_downgrade):
    installed_versions = installed_briefpilot_versions(install_dir)
    higher_versions = [
        version
        for version in installed_versions
        if validate_release_metadata.compare_versions(target_version, version) < 0
    ]
    current_version = highest_version(higher_versions) if higher_versions else None
    if (
        current_version
        and not allow_downgrade
    ):
        return downgrade_refusal_message(target_version, current_version)
    return None


def current_installed_version(install_dir, findings=None):
    installed_versions = installed_briefpilot_versions(install_dir, findings=findings)
    return highest_version(installed_versions) if installed_versions else None


def install_staged(staging_root, install_dir):
    install_dir = Path(install_dir).resolve()
    if not can_write_install_dir(install_dir):
        return False

    try:
        install_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".briefpilot-install-", dir=install_dir) as batch_tmp:
            batch_root = Path(batch_tmp)
            for command in COMMANDS:
                shutil.copytree(staging_root / command, batch_root / command)

            install_findings = validate_skill_commands.validate_installed(batch_root)
            if install_findings:
                return False

            for command in COMMANDS:
                target = install_dir / command
                if target.exists() and not target.is_dir():
                    return False

            backup_root = Path(tempfile.mkdtemp(prefix=".briefpilot-backup-", dir=install_dir))
            moved = []
            installed = []
            try:
                for command in COMMANDS:
                    target = install_dir / command
                    backup = backup_root / command
                    if target.exists():
                        target.rename(backup)
                        moved.append((backup, target))

                for command in COMMANDS:
                    source = batch_root / command
                    target = install_dir / command
                    source.rename(target)
                    installed.append(target)

                shutil.rmtree(backup_root)
                return True
            except OSError:
                for target in reversed(installed):
                    if target.exists() or target.is_symlink():
                        remove_path(target)
                for backup, target in reversed(moved):
                    if backup.exists() and not target.exists():
                        backup.rename(target)
                return False
            finally:
                if backup_root.exists():
                    shutil.rmtree(backup_root, ignore_errors=True)
    except OSError:
        return False


def output_mode(args):
    if args.dry_run:
        return "dry_run"
    if args.install_dir:
        return "install"
    return "package"


def optional_path(path):
    return str(Path(path).resolve()) if path else None


def path_list(paths):
    return [str(Path(path).resolve()) for path in paths]


def safe_target_version(root):
    try:
        return validate_release_metadata.read_version(root)
    except (OSError, UnicodeDecodeError):
        return None


def package_result_payload(
    args,
    ok,
    message,
    findings=None,
    target_version=None,
    current_version=None,
    installed=False,
    artifacts=None,
    planned_artifacts=None,
):
    return {
        "ok": ok,
        "kind": "package_briefpilot_skills",
        "mode": output_mode(args),
        "target_version": target_version,
        "current_version": current_version,
        "downgrade_allowed": bool(args.allow_downgrade),
        "installed": bool(installed),
        "install_dir": optional_path(args.install_dir),
        "artifacts": path_list(artifacts or []),
        "planned_artifacts": path_list(planned_artifacts or []),
        "findings": findings or [],
        "message": message,
    }


def emit_json(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def emit_result(args, payload, text_lines):
    if args.output_format == "json":
        emit_json(payload)
    else:
        for line in text_lines:
            print(line)
    return 0 if payload["ok"] else 1


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Package BriefPilot command Skills.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="BriefPilot repository root.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_ROOT / "dist", help="Directory for .skill artifacts.")
    parser.add_argument("--staging-dir", type=Path, help="Optional empty staging directory to keep for inspection.")
    parser.add_argument("--install-dir", type=Path, help="Optional skills directory to repair or refresh.")
    parser.add_argument("--allow-downgrade", action="store_true", help="Allow --install-dir to replace a newer installed version.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show planned outputs without writing packages.")
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
    root = args.root.resolve()
    installed_metadata_findings = []
    target_version = safe_target_version(root)
    current_version = current_installed_version(args.install_dir, installed_metadata_findings) if args.install_dir else None

    prechecked_staging_root = None
    if args.staging_dir:
        try:
            prechecked_staging_root = ensure_safe_staging_dir(root, args.staging_dir)
        except ValueError as error:
            message = str(error)
            payload = package_result_payload(
                args,
                ok=False,
                message=message,
                findings=[message],
                target_version=target_version,
                current_version=current_version,
            )
            return emit_result(args, payload, [message])

    findings = validate_skill_commands.validate_source(root)
    findings.extend(validate_git_source(root))
    findings.extend(installed_metadata_findings)
    if findings:
        message = "invalid BriefPilot source package"
        payload = package_result_payload(
            args,
            ok=False,
            message=message,
            findings=findings,
            target_version=target_version,
            current_version=current_version,
        )
        return emit_result(args, payload, [f"{message}:", *[f"- {finding}" for finding in findings]])

    staging_context = None
    if args.staging_dir:
        staging_root = prechecked_staging_root
    else:
        staging_context = tempfile.TemporaryDirectory(prefix="briefpilot-skill-build-")
        staging_root = Path(staging_context.name)

    try:
        try:
            stage_skills(root, staging_root)
        except ValueError as error:
            message = str(error)
            payload = package_result_payload(
                args,
                ok=False,
                message=message,
                findings=[message],
                target_version=target_version,
                current_version=current_version,
            )
            return emit_result(args, payload, [message])

        installed_findings = validate_skill_commands.validate_installed(staging_root)
        if installed_findings:
            message = "invalid staged BriefPilot command package"
            payload = package_result_payload(
                args,
                ok=False,
                message=message,
                findings=installed_findings,
                target_version=target_version,
                current_version=current_version,
            )
            return emit_result(args, payload, [f"{message}:", *[f"- {finding}" for finding in installed_findings]])

        planned = [args.out_dir / f"{command}.skill" for command in COMMANDS]
        downgrade_refusal = None
        if args.install_dir:
            downgrade_refusal = downgrade_refusal_for_install(
                args.install_dir,
                target_version,
                args.allow_downgrade,
            )
        if downgrade_refusal:
            payload = package_result_payload(
                args,
                ok=False,
                message=downgrade_refusal,
                findings=[downgrade_refusal],
                target_version=target_version,
                current_version=current_version,
                planned_artifacts=planned,
            )
            return emit_result(args, payload, [downgrade_refusal])

        if args.dry_run:
            message = "valid BriefPilot command package"
            text_lines = [message, "planned artifacts:", *[f"- {path}" for path in planned]]
            if args.install_dir:
                text_lines.append(f"planned install dir: {args.install_dir}")
            payload = package_result_payload(
                args,
                ok=True,
                message=message,
                target_version=target_version,
                current_version=current_version,
                planned_artifacts=planned,
            )
            return emit_result(args, payload, text_lines)

        archives = package_staged(staging_root, args.out_dir)
        dist_findings = validate_skill_commands.validate_dist(args.out_dir, root)
        if dist_findings:
            message = "invalid generated .skill artifacts"
            payload = package_result_payload(
                args,
                ok=False,
                message=message,
                findings=dist_findings,
                target_version=target_version,
                current_version=current_version,
                artifacts=archives,
            )
            return emit_result(args, payload, [f"{message}:", *[f"- {finding}" for finding in dist_findings]])

        installed = False
        install_fallback_message = None
        if args.install_dir:
            installed = install_staged(staging_root, args.install_dir)
            if installed:
                install_findings = validate_skill_commands.validate_installed(args.install_dir)
                if install_findings:
                    message = "invalid repaired install"
                    payload = package_result_payload(
                        args,
                        ok=False,
                        message=message,
                        findings=install_findings,
                        target_version=target_version,
                        current_version=current_version,
                        installed=True,
                        artifacts=archives,
                    )
                    return emit_result(args, payload, [f"{message}:", *[f"- {finding}" for finding in install_findings]])
            else:
                install_fallback_message = "install dir is not writable or not safely replaceable; generated .skill artifacts instead"

        message = install_fallback_message or "packaged BriefPilot command Skills"
        text_lines = []
        if install_fallback_message:
            text_lines.append(install_fallback_message)
        text_lines.append("packaged BriefPilot command Skills:")
        text_lines.extend(f"- {archive}" for archive in archives)
        if args.install_dir and installed:
            text_lines.append(f"installed command Skills to: {args.install_dir}")
        payload = package_result_payload(
            args,
            ok=True,
            message=message,
            target_version=target_version,
            current_version=current_version,
            installed=installed,
            artifacts=archives,
        )
        return emit_result(args, payload, text_lines)
    finally:
        if staging_context is not None:
            staging_context.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
