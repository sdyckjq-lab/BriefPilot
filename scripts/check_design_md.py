#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import design_md_checks


MAX_DESIGN_MD_BYTES = 1_000_000
RAW_OUTPUT_LIMIT = 4000
MODES = {"fallback", "auto", "official"}
OFFICIAL_COMMAND_TIMEOUT_SECONDS = 20
DENIED_OFFICIAL_COMMAND_NAMES = {
    "bash",
    "bun",
    "bunx",
    "corepack",
    "env",
    "fish",
    "node",
    "npm",
    "npx",
    "pnpm",
    "python",
    "python3",
    "sh",
    "yarn",
    "zsh",
}


def validate_design_path(raw_path):
    path = Path(raw_path).expanduser()
    if not path.exists():
        return None, f"missing file: {raw_path}"
    if path.is_dir():
        return None, f"DESIGN.md path must be a Markdown file, not a directory: {raw_path}"
    if path.suffix.lower() != ".md":
        return None, f"DESIGN.md path must end in .md: {raw_path}"
    if path.is_symlink():
        return None, f"DESIGN.md path must not be a symlink: {raw_path}"
    if path.stat().st_size > MAX_DESIGN_MD_BYTES:
        return None, f"DESIGN.md path is too large: {raw_path}"
    return path.resolve(), None


def validate_official_command(raw_command):
    if not raw_command:
        return None, None
    command = Path(raw_command).expanduser()
    if not command.is_absolute():
        return None, "--official-command must be an absolute path to a local executable"
    try:
        resolved = command.resolve(strict=True)
    except (FileNotFoundError, OSError, RuntimeError):
        return None, f"--official-command does not point to a file: {raw_command}"
    if command.name in DENIED_OFFICIAL_COMMAND_NAMES or resolved.name in DENIED_OFFICIAL_COMMAND_NAMES:
        return None, "--official-command must point to a specific safe local lint executable, not a package manager, shell, or interpreter"
    if not resolved.is_file():
        return None, f"--official-command does not point to a file: {raw_command}"
    if not os.access(resolved, os.X_OK):
        return None, f"--official-command is not executable: {raw_command}"
    return resolved, None


def bounded_output(text):
    text = text or ""
    if len(text) <= RAW_OUTPUT_LIMIT:
        return text
    return text[:RAW_OUTPUT_LIMIT] + "\n[truncated]"


def command_environment(command):
    command_dir = str(Path(command).parent)
    existing_path = os.environ.get("PATH", os.defpath)
    return {
        "PATH": command_dir if not existing_path else command_dir + os.pathsep + existing_path,
        "LC_ALL": "C",
        "LANG": "C",
    }


def decode_output(output):
    return bytes(output).decode("utf-8", errors="replace")


def run_command(args, cwd):
    env = command_environment(args[0])
    output = bytearray()
    truncated = False
    process = subprocess.Popen(
        args,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert process.stdout is not None
    output_fd = process.stdout.fileno()
    os.set_blocking(output_fd, False)
    deadline = time.monotonic() + OFFICIAL_COMMAND_TIMEOUT_SECONDS
    try:
        while True:
            remaining_seconds = deadline - time.monotonic()
            if remaining_seconds <= 0:
                process.kill()
                process.wait()
                raise subprocess.TimeoutExpired(args, OFFICIAL_COMMAND_TIMEOUT_SECONDS, output=decode_output(output))

            try:
                chunk = os.read(output_fd, 4096)
            except BlockingIOError:
                if process.poll() is not None:
                    break
                time.sleep(min(0.01, remaining_seconds))
                continue

            if not chunk:
                if process.poll() is not None:
                    break
                time.sleep(min(0.01, remaining_seconds))
                continue

            if len(output) + len(chunk) > RAW_OUTPUT_LIMIT:
                output.extend(chunk[: RAW_OUTPUT_LIMIT - len(output)])
                truncated = True
                if process.poll() is None:
                    process.kill()
                break
            output.extend(chunk)

    finally:
        process.stdout.close()

    if truncated:
        process.wait()
        output.extend(b"\n[truncated]")
    else:
        process.wait()
    return subprocess.CompletedProcess(args, process.returncode, decode_output(output), "")

def official_tool_status(command, design_path, mode):
    status = {
        "available": bool(command),
        "command": str(command) if command else None,
        "version": None,
        "exit_status": None,
        "merged": False,
        "error": None,
        "raw_output": "",
    }
    findings = []
    if not command:
        if mode == "official":
            status["error"] = "official mode requires --official-command with a safe absolute local path"
            findings.append(
                design_md_checks.finding(
                    "blocking",
                    "official_tool_unavailable",
                    "official_tool",
                    status["error"],
                    "Run fallback mode or provide a safe absolute official command path.",
                    source="google_official",
                )
            )
        return status, findings

    try:
        version = run_command([str(command), "--version"], cwd=design_path.parent)
        status["version"] = (version.stdout or version.stderr).strip().splitlines()[0] if (version.stdout or version.stderr).strip() else None
    except (subprocess.SubprocessError, OSError) as exc:
        status["version"] = None
        status["error"] = f"could not read official tool version: {exc}"

    try:
        lint = run_command([str(command), "lint", str(design_path)], cwd=design_path.parent)
    except subprocess.TimeoutExpired:
        status["error"] = "official lint timed out"
        findings.append(
            design_md_checks.finding(
                "blocking" if mode == "official" else "warning",
                "official_lint_timeout",
                "official_tool",
                status["error"],
                "Use fallback report or rerun with a known working official tool.",
                source="google_official",
            )
        )
        return status, findings
    except OSError as exc:
        status["error"] = f"official lint failed to start: {exc}"
        findings.append(
            design_md_checks.finding(
                "blocking" if mode == "official" else "warning",
                "official_lint_error",
                "official_tool",
                status["error"],
                "Use fallback report or rerun with a known working official tool.",
                source="google_official",
            )
        )
        return status, findings

    status["exit_status"] = lint.returncode
    status["raw_output"] = bounded_output((lint.stdout + "\n" + lint.stderr).strip())
    status["merged"] = True
    if lint.returncode != 0:
        findings.append(
            design_md_checks.finding(
                "blocking",
                "official_lint_failed",
                "official_tool",
                "Official Google DESIGN.md lint returned a non-zero exit status.",
                "Read the official output and fix stricter lint findings.",
                source="google_official",
            )
        )
    return status, findings


def report_mode(requested_mode, official_status):
    if official_status.get("merged"):
        return "mixed"
    if requested_mode == "official":
        return "google_official"
    return "briefpilot_fallback"


def display_source_path(design_path):
    try:
        return str(design_path.relative_to(design_md_checks.repo_root()))
    except ValueError:
        return str(design_path)


def source_sha256(design_path):
    try:
        return hashlib.sha256(Path(design_path).read_bytes()).hexdigest()
    except OSError:
        return ""


def build_report(design_path, requested_mode="auto", official_command=None):
    analysis = design_md_checks.analyze_path(design_path)
    findings = list(analysis["findings"])
    command_for_mode = None if requested_mode == "fallback" else official_command
    official_status, official_findings = official_tool_status(command_for_mode, design_path, requested_mode)
    findings.extend(official_findings)
    if not official_status.get("merged") and requested_mode in {"auto", "fallback"}:
        findings.append(
            design_md_checks.finding(
                "info",
                "optional_official_check",
                "official_tool",
                "Google official DESIGN.md lint was not run; fallback checks were used.",
                "For stricter checks, provide a safe absolute --official-command path or run the official tool manually.",
            )
        )
    counts = design_md_checks.severity_counts(findings)
    directions = design_md_checks.style_directions_by_id()
    direction_id = analysis.get("reference_direction")
    direction = directions.get(direction_id, {}) if direction_id else {}
    blocking = counts["blocking"] > 0
    next_action = "fix_then_continue" if blocking else "continue"
    return {
        "schema_version": "1.0",
        "source_path": display_source_path(design_path),
        "source_sha256": source_sha256(design_path),
        "mode": report_mode(requested_mode, official_status),
        "official_tool": official_status,
        "reference_direction": {
            "id": direction_id or "",
            "name": direction.get("name", ""),
        },
        "summary": counts,
        "blocking": blocking,
        "next_action": next_action,
        "findings": findings,
        "generated_at": "deterministic",
    }


def markdown_safe(value):
    return html.escape(str(value or ""), quote=False).replace("\r", " ").replace("\n", " ")


def render_markdown(report):
    findings = report.get("findings", [])
    lines = [
        "# DESIGN.md Review",
        "",
        f"Mode: {markdown_safe(report['mode'])}",
        "",
        f"Blocking: {str(report['blocking']).lower()}",
        "",
        f"Reference direction: {markdown_safe(report['reference_direction'].get('id', ''))}",
        "",
        f"Source SHA-256: {markdown_safe(report.get('source_sha256', ''))}",
        "",
        "Severity counts:",
        "",
        f"- blocking: {report['summary'].get('blocking', 0)}",
        f"- warning: {report['summary'].get('warning', 0)}",
        f"- info: {report['summary'].get('info', 0)}",
        "",
        f"Next action: {report['next_action']}",
        "",
        "Official tool:",
        "",
        f"- available: {str(report['official_tool'].get('available', False)).lower()}",
        f"- command: {markdown_safe(report['official_tool'].get('command') or '')}",
        f"- merged: {str(report['official_tool'].get('merged', False)).lower()}",
        "",
        "## Findings",
        "",
    ]
    if findings:
        for item in findings:
            lines.append(
                "- {severity} [{rule_id}] {location}: {message} Fix: {suggested_fix}".format(
                    severity=markdown_safe(item.get("severity", "")),
                    rule_id=markdown_safe(item.get("rule_id", "")),
                    location=markdown_safe(item.get("location", "")),
                    message=markdown_safe(item.get("message", "")),
                    suggested_fix=markdown_safe(item.get("suggested_fix", "")),
                )
            )
    else:
        lines.append("- None")
    return "\n".join(lines).rstrip() + "\n"


def write_report(report, markdown_path, json_path):
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("design_md")
    parser.add_argument("--markdown-out")
    parser.add_argument("--json-out")
    parser.add_argument("--mode", choices=sorted(MODES), default="auto")
    parser.add_argument("--official-command")
    args = parser.parse_args(argv)

    design_path, error = validate_design_path(args.design_md)
    if error:
        print(error, file=sys.stderr)
        return 1
    official_command = None
    if args.mode != "fallback":
        official_command, error = validate_official_command(args.official_command)
        if error:
            print(error, file=sys.stderr)
            return 1
    if args.mode == "official" and not official_command:
        print("official mode requires --official-command with a safe absolute local path", file=sys.stderr)
        return 1

    report = build_report(design_path, requested_mode=args.mode, official_command=official_command)
    try:
        write_report(
            report,
            Path(args.markdown_out) if args.markdown_out else None,
            Path(args.json_out) if args.json_out else None,
        )
    except OSError as exc:
        print(f"could not write report: {exc}", file=sys.stderr)
        return 1
    if not args.markdown_out and not args.json_out:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
