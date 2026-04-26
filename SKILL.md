---
name: briefpilot
description: Design brief compiler and result-review loop for AI design workflows. Verified on one AI search SaaS landing page golden demo and one AI search workspace answer-detail review demo. Use when a user wants to turn a vague product or page request into a reusable design brief, Google-style DESIGN.md visual system, targeted prompts for huashu-design, Claude Design, and v0, a review checklist, and post-generation modification prompts.
---

# BriefPilot

Use BriefPilot before design generation starts, and use it again after generation when the user asks whether a downstream result is good enough or how to fix it.

## Core Rule

Do not directly generate the final design unless the user explicitly asks. First compile the user's request into a reusable brief. After a downstream tool generates a result, review that result against the same saved brief package before writing any modification prompt.

## Default Workflow

1. Read the user's request, existing project context, and any existing `DESIGN.md`.
2. Diagnose the request with the scoring rubric in `references/scoring-rubric.md`.
3. Identify missing high-value information.
4. Ask 3-7 questions in standard mode, or create visible assumptions in quick mode.
5. Offer three design strategies before choosing one final direction.
6. Match a local reference direction from `references/design-style-index.json` before creating a new `DESIGN.md`.
7. Generate `design-brief.md`, `design-brief.json`, `DESIGN.md` when needed, target prompts, and `review-checklist.md`.
8. Save outputs under `.briefpilot/` by default unless the user asks for a visible directory.

## Post-Generation Review Mode

Use this mode when the user provides a generated result, pasted result summary, screenshot description, rendered-page review, or local generated file.

1. Load the source brief package: `design-brief.json`, linked `DESIGN.md`, selected strategy, and `review-checklist.md`.
2. Gather result evidence: pasted summary, local `.txt`/`.md`/`.html`/`.json` file, screenshot reference, or an already-provided visual review.
3. If the brief package or result evidence is missing, ask for the missing material and do not create a formal review report yet.
4. Decide whether visual review evidence is available. Use image-capable review or an already-provided gstack visual review when available; otherwise record a text/file fallback.
5. Compare the result against the chosen strategy, original brief, `DESIGN.md`, and review checklist.
6. Choose one decision: `accept`, `tweak`, `revise_brief_then_regenerate`, or `regenerate_from_scratch`.
7. Save `result-review.md` and `result-review.json`. For every non-accepted result, also save a ready-to-use modification or regeneration prompt.

## Verified Scope

Verified examples:

- AI search SaaS landing page golden demo.
- AI search research workspace / answer detail review loop.

For other SaaS landing pages, app pages, dashboards, decks, social visuals, or creative tasks, label the output as adjacent trial coverage unless a matching example exists.

## Modes

- Quick mode: skip questions, generate explicit assumptions, then create outputs after confirmation.
- Standard mode: ask 3-7 focused questions, then create outputs after strategy confirmation.
- Expert mode: ask 8-12 focused questions for high-stakes design work.

## Resources

- Read `references/workflow.md` for the full process.
- Read `references/result-review-workflow.md` before reviewing generated results.
- Read `references/visual-review-routing.md` before recording visual review evidence.
- Read `references/asset-layout.md` before writing files.
- Read `references/design-md.md` before reading or creating `DESIGN.md`.
- Read `references/design-style-index.md` before choosing a `DESIGN.md` reference direction.
- Read `references/design-md-quality-rules.md` before judging `DESIGN.md` issues.
- Read `references/brief-schema.md` before creating `design-brief.json`.
- Read `references/scoring-rubric.md` before scoring.
- Read `references/question-bank.md` before interviewing.
- Read the relevant adapter reference before exporting a target prompt.
- Use templates in `templates/` for output structure.
- Use scripts in `scripts/` when deterministic validation or export is useful.
