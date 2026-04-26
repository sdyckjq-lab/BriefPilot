#!/usr/bin/env python3
import sys
from pathlib import Path

import design_md_checks


REQUIRED_HEADINGS = design_md_checks.CANONICAL_HEADINGS
split_front_matter = design_md_checks.split_front_matter
front_matter_has_color_entry = design_md_checks.front_matter_has_color_entry


def main(argv):
    if len(argv) != 2:
        print("usage: validate_design_md.py <DESIGN.md>", file=sys.stderr)
        return 1

    path = Path(argv[1])
    try:
        result = design_md_checks.analyze_path(path)
    except FileNotFoundError:
        print(f"missing file: {path}", file=sys.stderr)
        return 1

    blocking_findings = [item for item in result["findings"] if item.get("severity") == "blocking"]
    if blocking_findings:
        print("invalid DESIGN.md:")
        for item in blocking_findings:
            print(f"- {item['message']}")
        return 1

    print(f"valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
