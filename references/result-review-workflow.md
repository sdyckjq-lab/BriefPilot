# Result Review Workflow

Use this workflow after a downstream design tool has produced a result.

## Completion Standard

A review run is complete when the source package and result evidence are grounded, `result-review.md` and `result-review.json` are saved, and every non-accepted decision has a ready-to-use next prompt. Chat-only critique is a fallback, not a complete saved review.

## Pre-Review Blocking Path

Do not save a formal review report until the review has enough grounding.

- If the user gives a generated result but no source brief package, ask for `.briefpilot/`, `design-brief.json`, and the linked `DESIGN.md`.
- If the user gives a brief package but no result evidence, ask for a pasted summary, local result path, screenshot description, or already-provided visual review.
- If the linked `DESIGN.md` is missing, ask for it or ask whether to use the package's generated visual-system assumptions.
- If the selected strategy is unclear, ask for the saved `diagnosis-and-strategies.md` or the selected strategy name before judging.

## Evidence Types

Supported review evidence:

- `pasted_summary`: the user pastes or describes what the generated result did.
- `local_file`: a local `.txt`, `.md`, `.html`, or `.json` result file.
- `screenshot_reference`: a supplied screenshot or screenshot description.
- `gstack_report`: an already-provided visual review result from gstack.

Screenshots and gstack reports are evidence the agent records. BriefPilot does not actively open pages, capture screenshots, or invoke gstack in this phase.

## Review Sequence

1. Load `design-brief.json`, the linked `DESIGN.md`, selected strategy, and `review-checklist.md`.
2. Read the generated-result evidence.
3. Record visual review availability using `references/visual-review-routing.md`.
4. Compare the result against the selected strategy, brief goals, page or app structure, `DESIGN.md`, and review checklist.
5. Separate execution issues from source-brief problems.
6. Choose the review decision.
7. Save the review artifacts and export the next prompt when needed.

## Decision Table

| Decision | Use when | Next artifact |
|---|---|---|
| `accept` | The core goal, page or app structure, visual rules, required states, and critical checks are satisfied. Minor polish is not blocking. | Save review only. No modification prompt required. |
| `tweak` | The direction is right and local fixes are enough. The selected strategy and `DESIGN.md` remain valid. | Export a targeted modification prompt. |
| `revise_brief_then_regenerate` | The result failed because the source brief missed or misstated necessary guidance. Preserve the selected strategy unless the review explicitly says the strategy is wrong. | Save `brief-revision.md`, then export a revised generation prompt. |
| `regenerate_from_scratch` | The result ignored the page type, selected strategy, structure, or visual system enough that local edits would be slower or misleading. | Export a full regeneration prompt. |

## Required Review Outputs

Write review artifacts under the project directory:

```text
reviews/
  result-review.md
  result-review.json
  brief-revision.md
prompts/
  <target>-modification.txt
```

`brief-revision.md` is required only for `revise_brief_then_regenerate`.

## Result Review JSON Contract

Use `templates/result-review.json` as the saved JSON shape. The contract is:

- `schema_version`: required string starting with `1`.
- `source.brief_path`: required repo-relative or package-relative path to `design-brief.json`.
- `source.design_md_path`: required path to the `DESIGN.md` that belongs to the reviewed brief package.
- `target_tool`: required enum: `huashu-design`, `claude-design`, `v0`, or `generic`.
- `evidence.kind`: required enum: `pasted_summary`, `local_file`, `screenshot_reference`, or `gstack_report`.
- `evidence.summary`: required non-empty text describing what was reviewed.
- `evidence.path`: required for `local_file`, optional for screenshot or gstack references, and not required for `pasted_summary`.
- `decision`: required enum: `accept`, `tweak`, `revise_brief_then_regenerate`, or `regenerate_from_scratch`.
- `selected_strategy`: required text naming the strategy being evaluated.
- `strategy_preserved`: required boolean. False requires `strategy_change_reason` and a decision that revises or regenerates.
- `findings`: required array for every non-`accept` decision. Each finding needs `severity`, `brief_reference`, `issue`, `evidence`, and `recommended_change`.
- `visual_review.status`: required enum: `available_model_image`, `available_gstack`, `not_provided`, or `unavailable`.
- `visual_review.source`: required when visual review was available.
- `visual_review.notes`: required text explaining either visual evidence or fallback.
- `brief_revision_path`: required only for `revise_brief_then_regenerate`.
- `prompt_intent`: required for non-accepted reviews: `targeted_modification`, `brief_revision_regeneration`, or `full_regeneration`.
- `prompt.keep`, `prompt.change`, and `prompt.acceptance_checks`: required non-empty arrays for non-accepted reviews.

## Decision To Prompt Mapping

- `accept`: no `prompt_intent` or modification prompt is required.
- `tweak`: use `prompt_intent: targeted_modification`.
- `revise_brief_then_regenerate`: use `prompt_intent: brief_revision_regeneration` and include `brief_revision_path`.
- `regenerate_from_scratch`: use `prompt_intent: full_regeneration`.

## Source Package Consistency

The review JSON, source brief JSON, linked `DESIGN.md`, and selected strategy must describe the same saved brief package. `source.design_md_path` must resolve to the same file as `design_system.design_md_path` in the source brief.

## Visual Evidence Consistency

- `gstack_report` requires `visual_review.status: available_gstack` and a source.
- `screenshot_reference` requires a screenshot source and either `available_model_image` or a clear `unavailable` fallback note.
- `not_provided` cannot be used with screenshot or gstack evidence.

## Finding Rules

Each finding must name the brief, strategy, `DESIGN.md`, or checklist reference that makes the issue real. Do not write taste-only critique. For non-accepted reviews, include what to keep, what to change, and acceptance checks for the next generation run.

## Visual Review Checklist

When visual evidence is available, check:

- First-glance page identity: the user can tell what the page or screen is for.
- Hierarchy: answer, source list, confidence, and actions are visually distinct.
- Source detail discoverability: source titles, excerpts, links, and detail panels are findable.
- State differences: empty, loading, success, error, low-confidence, and unavailable states look meaningfully different.
- Mobile fit: content stacks without overlap or horizontal scrolling.
- `DESIGN.md` alignment: colors, typography, radius, spacing, and forbidden directions are respected.

If visual review is unavailable, record the fallback in `visual_review.notes` and continue with text/file evidence.
