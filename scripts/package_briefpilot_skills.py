#!/usr/bin/env python3
import argparse
import json
import os
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


def build_manifest(root):
    return {
        "schema_version": "1.0",
        "package": "BriefPilot",
        "commands": list(COMMANDS),
        "package_version": validate_release_metadata.read_version(root),
        "source_remote": OFFICIAL_SOURCE_REMOTE,
        "source_commit": git_value(root, "rev-parse", "--short", "HEAD"),
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


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Package BriefPilot command Skills.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="BriefPilot repository root.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_ROOT / "dist", help="Directory for .skill artifacts.")
    parser.add_argument("--staging-dir", type=Path, help="Optional empty staging directory to keep for inspection.")
    parser.add_argument("--install-dir", type=Path, help="Optional skills directory to repair or refresh.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show planned outputs without writing packages.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()

    findings = validate_skill_commands.validate_source(root)
    if findings:
        print("invalid BriefPilot source package:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    staging_context = None
    if args.staging_dir:
        try:
            staging_root = ensure_safe_staging_dir(root, args.staging_dir)
        except ValueError as error:
            print(error)
            return 1
    else:
        staging_context = tempfile.TemporaryDirectory(prefix="briefpilot-skill-build-")
        staging_root = Path(staging_context.name)

    try:
        try:
            stage_skills(root, staging_root)
        except ValueError as error:
            print(error)
            return 1

        installed_findings = validate_skill_commands.validate_installed(staging_root)
        if installed_findings:
            print("invalid staged BriefPilot command package:")
            for finding in installed_findings:
                print(f"- {finding}")
            return 1

        planned = [args.out_dir / f"{command}.skill" for command in COMMANDS]
        if args.dry_run:
            print("valid BriefPilot command package")
            print("planned artifacts:")
            for path in planned:
                print(f"- {path}")
            if args.install_dir:
                print(f"planned install dir: {args.install_dir}")
            return 0

        archives = package_staged(staging_root, args.out_dir)
        dist_findings = validate_skill_commands.validate_dist(args.out_dir, root)
        if dist_findings:
            print("invalid generated .skill artifacts:")
            for finding in dist_findings:
                print(f"- {finding}")
            return 1

        installed = False
        if args.install_dir:
            installed = install_staged(staging_root, args.install_dir)
            if installed:
                install_findings = validate_skill_commands.validate_installed(args.install_dir)
                if install_findings:
                    print("invalid repaired install:")
                    for finding in install_findings:
                        print(f"- {finding}")
                    return 1
            else:
                print("install dir is not writable or not safely replaceable; generated .skill artifacts instead")

        print("packaged BriefPilot command Skills:")
        for archive in archives:
            print(f"- {archive}")
        if args.install_dir and installed:
            print(f"installed command Skills to: {args.install_dir}")
        return 0
    finally:
        if staging_context is not None:
            staging_context.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
