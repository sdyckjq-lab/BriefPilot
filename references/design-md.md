# DESIGN.md

Use `DESIGN.md` as BriefPilot's default reusable visual system format.

## Role

`design-brief.md` explains what the project should achieve.

`DESIGN.md` explains what the product or brand should look and feel like.

## Read Before Creating

Before generating a new `DESIGN.md`, search the current project and `.briefpilot/brands/` for an existing file named `DESIGN.md`.

If one exists, reuse it and summarize the relevant visual guidance in exported prompts.

If none exists, match the task to a local reference direction in `design-style-index.json`, then generate a complete first version and mark uncertain choices as assumptions.

Use `design-style-index.md` to choose the direction. Reference mechanisms, not brands. Do not copy external `DESIGN.md` files, design-system docs, logos, proprietary fonts, screenshots, or full color systems.

## File Structure

Use YAML front matter for machine-readable tokens and Markdown sections for human-readable rationale.

Required sections:

1. `## Overview`
2. `## Visual Theme`
3. `## Colors`
4. `## Typography`
5. `## Layout`
6. `## Elevation & Depth`
7. `## Shapes`
8. `## Components`
9. `## Responsive Behavior`
10. `## Motion & Feedback`
11. `## Content Voice`
12. `## Do's and Don'ts`
13. `## Reference Direction`
14. `## Agent Guidance`

## YAML Token Groups

Support these token groups:

```yaml
---
version: alpha
name: Example Brand
description: Short visual system summary.
colors:
  primary: "#1A1C1E"
typography:
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  md: 8px
spacing:
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
---
```

## Rules

- Keep token values exact when the user provides them.
- Use assumptions only when the user has not provided visual details.
- Prefer a stable token set over many speculative tokens, but include enough role-based tokens for real product states.
- Do not invent logos, customer assets, or proprietary brand claims.
- Include practical do's and don'ts that downstream agents can follow.
- Include responsive behavior, motion, content voice, accessibility, and page/data state guidance.
- Include the chosen reference direction and source-boundary reminder.
- Run `scripts/validate_design_md.py` for the built-in fallback check.
- Run `scripts/check_design_md.py` when a saved Markdown and JSON design review report is needed.
- Treat Google `@google/design.md` lint/diff/export/spec as optional enhancements. BriefPilot does not silently install npm packages and does not automatically run `npx`.

## Optional Official Google Checks

BriefPilot's automatic checks work without Node/npm. To use Google's stricter lint path, provide a safe absolute local command path:

```text
python3 scripts/check_design_md.py DESIGN.md --mode auto --official-command /absolute/path/to/design.md --markdown-out reviews/design-md-review.md --json-out reviews/design-md-review.json
```

The report writer wraps official `lint` only in this version. Official `diff`, `export`, and `spec` remain manual user-run commands and future extension points.
