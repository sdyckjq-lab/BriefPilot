# Asset Layout

## Default Output Directory

Use `.briefpilot/` by default.

```text
.briefpilot/
  brands/
  projects/
```

## Project Assets

Project content is Chinese-first by default. Record the language in `design-brief.json` under `meta.content_language`; keep the file layout and technical filenames in English.

Write project assets to:

```text
.briefpilot/projects/<project-slug>/
```

Required files:

```text
diagnosis-and-strategies.md
design-brief.md
design-brief.json
DESIGN.md
design-md-quality-proof.md
review-checklist.md
prompts/huashu-design.txt
prompts/claude-design.txt
prompts/v0.txt
reviews/design-md-review.md
reviews/design-md-review.json
```

Write `assumptions.md` when quick mode or unresolved assumptions are used.

Write `DESIGN.md` in the project directory when it is generated for that project. If a reusable brand `DESIGN.md` already exists, store it under `brands/` and point `design_system.design_md_path` at that file instead.

Write `reviews/design-md-review.md` and `reviews/design-md-review.json` when running a `DESIGN.md` quality check. Checked-in examples use forced fallback mode so they do not depend on Node/npm or local Google tooling.

## Review Assets

When reviewing a downstream generated result, write review artifacts beside the source brief package:

```text
reviews/result-review.md
reviews/result-review.json
reviews/brief-revision.md
prompts/<target>-modification.txt
```

`brief-revision.md` is required only when the decision is `revise_brief_then_regenerate`. `accept` saves the review report but does not require a modification prompt. `tweak` keeps the selected strategy and exports a targeted modification prompt. `regenerate_from_scratch` exports a full regeneration prompt.

## Brand Assets

Use lightweight brand context only in MVP.

Phase 1 may store or reuse a single `DESIGN.md` reference. It does not provide brand workspace management, project history, brand CRUD, brand discovery, or multi-brand reuse behavior.

Write brand assets to:

```text
.briefpilot/brands/<brand-slug>/
```

Supported files:

```text
DESIGN.md
reviews/design-md-review.md
reviews/design-md-review.json
```

`DESIGN.md` is the canonical visual system file. `brand-context.json` and stronger brand reuse conventions are deferred to Phase 2.

## Visible Directory Override

If the user asks for a visible directory, use the requested directory instead of `.briefpilot/`.

Example:

```text
design-briefs/<project-slug>/
```

## Slugs

Use lowercase letters, digits, and hyphens. Convert spaces and punctuation to hyphens.
