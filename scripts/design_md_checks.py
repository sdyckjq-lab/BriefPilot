#!/usr/bin/env python3
import json
import re
from pathlib import Path


CANONICAL_HEADINGS = [
    "## Overview",
    "## Colors",
    "## Typography",
    "## Layout",
    "## Elevation & Depth",
    "## Shapes",
    "## Components",
    "## Do's and Don'ts",
]

QUALITY_HEADINGS = [
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
]

REQUIRED_TOKEN_GROUPS = ["colors", "typography", "rounded", "spacing", "components"]
REQUIRED_COLOR_ROLES = [
    "background",
    "surface",
    "text",
    "muted_text",
    "border",
    "primary_action",
    "success",
    "warning",
    "danger",
    "info",
]
TYPOGRAPHY_LEVELS = ["display", "title", "heading", "body", "caption", "label"]
COMPONENT_STATES = ["default", "hover", "pressed", "disabled", "focus", "error"]
PAGE_STATES = ["loading", "empty", "success", "error"]
ACCESSIBILITY_TERMS = ["keyboard", "focus", "44px", "touch", "reduced motion"]
TOKEN_REF_RE = re.compile(r"\{([A-Za-z0-9_.-]+)\}")
HEADING_RE = re.compile(r"^## .+$", re.MULTILINE)
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def repo_root():
    return Path(__file__).resolve().parents[1]


def split_front_matter(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :]


def parse_scalar(value):
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_front_matter(front_matter):
    data = {}
    errors = []
    stack = [(-1, data)]
    for line_number, raw_line in enumerate(front_matter.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.lstrip().startswith("- "):
            errors.append(f"unsupported YAML list item at front matter line {line_number}")
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if "\t" in raw_line[:indent]:
            errors.append(f"tabs are not supported in front matter line {line_number}")
            continue
        if ":" not in raw_line:
            errors.append(f"missing ':' in front matter line {line_number}")
            continue
        key, raw_value = raw_line.strip().split(":", 1)
        if not key:
            errors.append(f"empty key in front matter line {line_number}")
            continue
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else data
        if not isinstance(parent, dict):
            errors.append(f"unsupported nested value at front matter line {line_number}")
            continue
        if raw_value.strip():
            parent[key] = parse_scalar(raw_value)
        else:
            child = {}
            parent[key] = child
            stack.append((indent, child))
    return data, errors


def flatten_tokens(value, prefix=""):
    items = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(child, dict):
                items.update(flatten_tokens(child, path))
            else:
                items[path] = child
    return items


def token_at(tokens, dotted_path):
    current = tokens
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def resolve_value(value, tokens, seen=None):
    if not isinstance(value, str):
        return value
    matches = TOKEN_REF_RE.findall(value)
    if not matches:
        return value
    seen = seen or set()
    resolved = value
    for ref in matches:
        if ref in seen:
            return value
        token_value = token_at(tokens, ref)
        if token_value is None:
            return value
        resolved = resolved.replace("{" + ref + "}", str(resolve_value(token_value, tokens, seen | {ref})))
    return resolved


def finding(severity, rule_id, location, message, suggested_fix, source="briefpilot_fallback"):
    return {
        "severity": severity,
        "rule_id": rule_id,
        "location": location,
        "message": message,
        "suggested_fix": suggested_fix,
        "source": source,
    }


def headings_in(body):
    return [match.group(0).strip() for match in HEADING_RE.finditer(body)]


def section_order_findings(body):
    findings = []
    for required in CANONICAL_HEADINGS:
        if required not in body:
            findings.append(
                finding(
                    "blocking",
                    "missing_canonical_section",
                    required,
                    f"Missing canonical section: {required}",
                    "Add the section in the canonical DESIGN.md order.",
                )
            )
    positions = [body.find(heading) for heading in CANONICAL_HEADINGS if heading in body]
    if positions != sorted(positions):
        findings.append(
            finding(
                "blocking",
                "section_order",
                "Markdown body",
                "Canonical sections are not in the required order.",
                "Reorder the canonical DESIGN.md sections.",
            )
        )
    for heading in QUALITY_HEADINGS:
        if heading not in body:
            findings.append(
                finding(
                    "warning",
                    "missing_quality_section",
                    heading,
                    f"Missing high-quality guidance section: {heading}",
                    "Add the section when generating upgraded BriefPilot DESIGN.md files.",
                )
            )
    return findings


def front_matter_has_color_entry(front_matter):
    tokens, _ = parse_front_matter(front_matter or "")
    colors = tokens.get("colors")
    return isinstance(colors, dict) and bool(colors)


def token_findings(tokens):
    findings = []
    for group in REQUIRED_TOKEN_GROUPS:
        if not isinstance(tokens.get(group), dict) or not tokens.get(group):
            findings.append(
                finding(
                    "blocking",
                    "missing_token_group",
                    f"front_matter.{group}",
                    f"Missing required token group: {group}",
                    "Add the required token group to front matter.",
                )
            )

    colors = tokens.get("colors") if isinstance(tokens.get("colors"), dict) else {}
    for role in REQUIRED_COLOR_ROLES:
        value = colors.get(role)
        if value is None:
            findings.append(
                finding(
                    "blocking",
                    "missing_color_role",
                    f"front_matter.colors.{role}",
                    f"Missing required role-based color: {role}",
                    "Add the semantic color role.",
                )
            )
        elif not isinstance(value, str) or not HEX_RE.match(value):
            findings.append(
                finding(
                    "blocking",
                    "invalid_required_color",
                    f"front_matter.colors.{role}",
                    f"Invalid required color value for {role}: {value}",
                    "Use a #RGB or #RRGGBB hex color.",
                )
            )

    for path, value in flatten_tokens(colors, "colors").items():
        if isinstance(value, str) and value.startswith("#") and not HEX_RE.match(value):
            severity = "blocking" if path.split(".")[-1] in REQUIRED_COLOR_ROLES else "warning"
            findings.append(
                finding(
                    severity,
                    "invalid_color",
                    f"front_matter.{path}",
                    f"Invalid color value: {value}",
                    "Use a #RGB or #RRGGBB hex color.",
                )
            )

    typography = tokens.get("typography") if isinstance(tokens.get("typography"), dict) else {}
    for level in TYPOGRAPHY_LEVELS:
        if level not in typography:
            findings.append(
                finding(
                    "warning",
                    "missing_typography_level",
                    f"front_matter.typography.{level}",
                    f"Missing typography level: {level}",
                    "Add a complete display/title/heading/body/caption/label hierarchy.",
                )
            )
    return findings


def broken_reference_findings(text, tokens):
    findings = []
    for ref in sorted(set(TOKEN_REF_RE.findall(text))):
        if token_at(tokens, ref) is None:
            findings.append(
                finding(
                    "blocking",
                    "broken_token_reference",
                    ref,
                    f"Broken token reference: {{{ref}}}",
                    "Add the referenced token or update the reference path.",
                )
            )
    return findings


def hex_to_rgb(value):
    value = value.strip()
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if not HEX_RE.match(value):
        return None
    return tuple(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5))


def relative_luminance(rgb):
    values = []
    for channel in rgb:
        if channel <= 0.03928:
            values.append(channel / 12.92)
        else:
            values.append(((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]


def contrast_ratio(first, second):
    first_rgb = hex_to_rgb(first)
    second_rgb = hex_to_rgb(second)
    if not first_rgb or not second_rgb:
        return None
    first_l = relative_luminance(first_rgb)
    second_l = relative_luminance(second_rgb)
    lighter = max(first_l, second_l)
    darker = min(first_l, second_l)
    return (lighter + 0.05) / (darker + 0.05)


def contrast_findings(tokens):
    findings = []
    components = tokens.get("components") if isinstance(tokens.get("components"), dict) else {}
    for name, config in components.items():
        if not isinstance(config, dict):
            continue
        background = resolve_value(config.get("backgroundColor"), tokens)
        text = resolve_value(config.get("textColor"), tokens)
        if not isinstance(background, str) or not isinstance(text, str):
            continue
        ratio = contrast_ratio(background, text)
        if ratio is not None and ratio < 4.5:
            findings.append(
                finding(
                    "warning",
                    "low_contrast",
                    f"front_matter.components.{name}",
                    f"Component contrast is {ratio:.2f}:1, below 4.5:1.",
                    "Adjust component text or background color for readable contrast.",
                )
            )
    return findings


def prose_findings(body):
    findings = []
    lower = body.lower()
    for term in COMPONENT_STATES:
        if term not in lower:
            findings.append(
                finding(
                    "warning",
                    "missing_component_state",
                    "## Components",
                    f"Component guidance does not mention {term} state.",
                    "Add practical component state guidance.",
                )
            )
    for term in PAGE_STATES:
        if term not in lower:
            findings.append(
                finding(
                    "warning",
                    "missing_page_state",
                    "Markdown body",
                    f"Page or data state guidance does not mention {term}.",
                    "Add state guidance for generated pages or app surfaces.",
                )
            )
    for term in ACCESSIBILITY_TERMS:
        if term not in lower:
            findings.append(
                finding(
                    "warning",
                    "missing_accessibility_guidance",
                    "Markdown body",
                    f"Accessibility guidance does not mention {term}.",
                    "Add explicit accessibility guidance.",
                )
            )
    if "## Motion & Feedback" not in body:
        findings.append(
            finding(
                "warning",
                "missing_motion_guidance",
                "## Motion & Feedback",
                "Motion and feedback guidance is missing.",
                "Add restrained motion and reduced-motion guidance.",
            )
        )
    if "## Content Voice" not in body:
        findings.append(
            finding(
                "warning",
                "missing_content_voice",
                "## Content Voice",
                "Content voice guidance is missing.",
                "Add tone and copy guidance.",
            )
        )
    return findings


def load_style_index():
    path = Path(__file__).resolve().parents[1] / "references" / "design-style-index.json"
    return json.loads(path.read_text(encoding="utf-8"))


def style_directions_by_id():
    return {item["id"]: item for item in load_style_index().get("directions", [])}


def reference_direction(body, tokens):
    design_system = tokens.get("design_system")
    if isinstance(design_system, dict):
        direction = design_system.get("reference_direction")
        if isinstance(direction, dict) and direction.get("id"):
            return direction.get("id")
        if isinstance(direction, str) and direction:
            return direction
    match = re.search(r"Reference direction:\s*`([^`]+)`", body, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"reference direction:\s*([a-z0-9_-]+)", body, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return None


DRIFT_KEYWORDS = {
    "product_proof": ["product surface", "mock", "demo", "proof", "screenshot"],
    "conversion_path": ["cta", "signup", "trial", "demo", "conversion"],
    "technical_artifact": ["code", "api", "command", "sdk", "cli"],
    "copyable_flow": ["copy", "install", "quickstart", "docs"],
    "stateful_surface": ["loading", "empty", "success", "error", "permission", "unavailable"],
    "data_density": ["table", "panel", "row", "metadata", "source", "detail"],
    "navigation_model": ["search", "nav", "breadcrumb", "article"],
    "money_state": ["confirmation", "failed", "pending", "risk", "receipt"],
    "editing_controls": ["toolbar", "canvas", "selection", "undo", "export"],
    "touch_first": ["touch", "mobile", "onboarding", "feedback"],
    "purchase_path": ["price", "variant", "cart", "checkout", "product"],
    "reading_path": ["reading", "line length", "byline", "article", "media"],
    "task_completion": ["task", "completion", "reminder", "quick", "saved"],
    "shared_state": ["owner", "comment", "status", "approval", "activity"],
    "subject_visibility": ["product", "gallery", "media", "object", "showcase"],
}


def reference_findings(body, tokens, strict_reference=False):
    findings = []
    lower = body.lower()
    directions = style_directions_by_id()
    direction_id = reference_direction(body, tokens)
    if not direction_id:
        findings.append(
            finding(
                "blocking" if strict_reference else "warning",
                "missing_reference_direction",
                "## Reference Direction",
                "Missing local reference direction.",
                "Choose a direction from design-style-index.json and explain the source boundary.",
            )
        )
        return None, findings
    if direction_id not in directions:
        findings.append(
            finding(
                "blocking",
                "unknown_reference_direction",
                "## Reference Direction",
                f"Unknown reference direction: {direction_id}",
                "Use an id from design-style-index.json.",
            )
        )
        return direction_id, findings

    if direction_id == "enterprise_data_workspace" and ("decorative hero-only" in lower or "marketing hero only" in lower):
        findings.append(
            finding(
                "blocking",
                "reference_direction_conflict",
                "## Reference Direction",
                "Enterprise data workspace direction conflicts with decorative hero-only guidance.",
                "Use signed-in data workspace guidance or choose ai_product_landing_page.",
            )
        )
    for check in directions[direction_id].get("drift_checks", []):
        keywords = DRIFT_KEYWORDS.get(check.get("id"), [])
        if keywords and not any(keyword in lower for keyword in keywords):
            findings.append(
                finding(
                    "warning",
                    "reference_direction_drift",
                    f"drift_checks.{check.get('id')}",
                    check.get("warning", "The DESIGN.md may drift from the selected direction."),
                    "Add guidance that matches the selected reference direction, or choose a better direction.",
                )
            )
    return direction_id, findings


def brand_copy_findings(body):
    findings = []
    for line_number, line in enumerate(body.splitlines(), start=1):
        lower = line.lower()
        if any(skip in lower for skip in ["do not copy", "don't copy", "never copy", "not copy", "do not clone"]):
            continue
        risky = (
            re.search(r"\bclone\s+[A-Z][A-Za-z0-9& .'-]+", line)
            or re.search(r"\bcopy\b.*\b(logo|brand identity|brand system|page|app|typeface)\b", lower)
            or re.search(r"\buse\b.*\b(logo|proprietary font|proprietary typeface|exact brand identity)\b", lower)
            or "exact brand identity" in lower
        )
        if risky:
            findings.append(
                finding(
                    "blocking",
                    "brand_copy_risk",
                    f"line {line_number}",
                    "Direct brand-copy instruction detected.",
                    "Rewrite as abstract reference mechanisms and remove requests to copy protected brand assets.",
                )
            )
    return findings


def severity_counts(findings):
    counts = {"blocking": 0, "warning": 0, "info": 0}
    for item in findings:
        severity = item.get("severity")
        if severity in counts:
            counts[severity] += 1
    return counts


def analyze_text(text, source_path="", strict_reference=False):
    findings = []
    front_matter, body = split_front_matter(text)
    tokens = {}
    parse_errors = []
    if front_matter is None:
        findings.append(
            finding(
                "blocking",
                "missing_front_matter",
                "front_matter",
                "Missing YAML front matter delimited by ---.",
                "Add front matter with required token groups.",
            )
        )
    else:
        tokens, parse_errors = parse_front_matter(front_matter)
        for error in parse_errors:
            findings.append(
                finding(
                    "blocking",
                    "front_matter_parse_error",
                    "front_matter",
                    error,
                    "Use the supported nested key/value front matter subset.",
                )
            )
        if "name" not in tokens:
            findings.append(
                finding(
                    "blocking",
                    "missing_name",
                    "front_matter.name",
                    "Missing name: in front matter.",
                    "Add a visual system name.",
                )
            )
    findings.extend(section_order_findings(body))
    findings.extend(token_findings(tokens))
    findings.extend(broken_reference_findings(text, tokens))
    findings.extend(contrast_findings(tokens))
    findings.extend(prose_findings(body))
    direction_id, direction_findings = reference_findings(body, tokens, strict_reference=strict_reference)
    findings.extend(direction_findings)
    findings.extend(brand_copy_findings(body))
    counts = severity_counts(findings)
    return {
        "source_path": str(source_path),
        "front_matter": front_matter,
        "tokens": tokens,
        "body": body,
        "headings": headings_in(body),
        "reference_direction": direction_id,
        "findings": findings,
        "summary": {
            "blocking": counts["blocking"],
            "warning": counts["warning"],
            "info": counts["info"],
        },
        "blocking": counts["blocking"] > 0,
    }


def unreadable_analysis(path, message):
    item = finding(
        "blocking",
        "design_md_unreadable",
        "DESIGN.md",
        message,
        "Use a readable UTF-8 Markdown file.",
    )
    return {
        "source_path": str(path),
        "front_matter": None,
        "tokens": {},
        "body": "",
        "headings": [],
        "reference_direction": None,
        "findings": [item],
        "summary": {
            "blocking": 1,
            "warning": 0,
            "info": 0,
        },
        "blocking": True,
    }


def analyze_path(path, strict_reference=False):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return unreadable_analysis(path, f"Missing DESIGN.md file: {path}")
    except UnicodeDecodeError as exc:
        return unreadable_analysis(path, f"DESIGN.md is not readable UTF-8 text: {exc}")
    except OSError as exc:
        return unreadable_analysis(path, f"DESIGN.md cannot be read: {exc}")
    return analyze_text(text, source_path=path, strict_reference=strict_reference)
