# BriefPilot Workflow

## Completion Standard

A BriefPilot run is complete when the reusable brief package is saved to disk. Chat-only output is a blocked fallback for environments without filesystem access; record that blocker and do not mark the run fully complete.

For post-generation result review, use `result-review-workflow.md`. A review run is complete only when the review artifacts are saved and every non-accepted decision has a next prompt.

## Step 1: Diagnose

Identify:

- Task type
- Brief Score
- Missing information
- Generation risks
- Recommended mode

Phase 1 verified task type:

- AI search SaaS landing page golden demo

Phase 2 candidate task types:

- Other SaaS landing pages
- App prototype
- Web app dashboard
- Pitch deck
- Product launch kit
- Social visual content
- Infographic
- Product demo page
- Brand visual exploration
- Design review
- Unknown design task

## Step 2: Choose Mode

Use quick mode when the user wants speed or does not want questions.

Use standard mode by default.

Use expert mode for high-stakes, broad, or brand-sensitive work.

## Step 3: Fill Gaps

For standard and expert mode, ask focused questions from `question-bank.md`.

For quick mode, create assumptions and label them as assumptions.

## Step 4: Offer Three Strategies

Each strategy must include:

- Name
- Best use case
- Visual tone
- Information structure focus
- Risk
- Best target tools
- Reference direction from `design-style-index.json` when a visual system will be generated

## Step 5: Confirm Direction

Ask the user to choose one strategy, combine strategies, or revise the strategies.

## Step 6: Generate Assets

Default user-facing content is Simplified Chinese (`zh-CN`) unless the user asks for another language. Keep filenames, JSON keys, commands, tool names, component names, and design token keys in English. Every `design-brief.json` must include `meta.content_language`.

Write:

- `diagnosis-and-strategies.md`
- `design-brief.md`
- `design-brief.json`
- `DESIGN.md` when no usable project or brand `DESIGN.md` exists
- target prompts
- `review-checklist.md`
- `assumptions.md` when assumptions were used

## Step 7: Validate

Run `scripts/validate_brief.py` on the generated JSON brief when scripts can be executed.

Run `scripts/validate_design_md.py` on generated `DESIGN.md` when scripts can be executed.

Run `scripts/check_design_md.py` when a saved `design-md-review.md` and `design-md-review.json` report is needed.

Run `scripts/export_prompt.py` for at least one adapter when scripts can be executed.

Run `scripts/validate_golden_demo.py` when checking the included golden example or a full example package.

## Post-Generation Branch

When the user asks to evaluate a generated result, do not restart the brief workflow. Load the saved source package, gather result evidence, follow `result-review-workflow.md`, and save review artifacts under the same project directory.
