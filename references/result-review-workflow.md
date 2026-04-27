# Result Review Workflow

Use this workflow after a downstream design tool has produced a result.

## Completion Standard

A review run is complete when the source package and result evidence are grounded, `result-review.md`, `result-review.json`, and any needed `review-next-actions.md` are saved, and every non-accepted decision has exactly one recommended next action. Chat-only critique is a fallback, not a complete saved review.

Review is review-only by default. If the user says "review", "看看", "检查", "帮我看下", or similar, BriefPilot may save review artifacts, but must not edit source brief files, `design-spec.md`, generated result files, or local code.

Direct local repair is a separate follow-up mode. Before editing anything, BriefPilot must list the exact files it plans to edit and wait for explicit confirmation. A broad request such as "帮我改好" is not enough by itself.

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

Screenshots, image-only mockups, Figma exports, external-platform drafts, and pasted summaries are not directly editable by BriefPilot. They can produce review reports, external modification prompts, or spec revisions.

## Review Sequence

1. Load `design-brief.json`, the linked `DESIGN.md`, selected strategy, and `review-checklist.md`.
2. Read the generated-result evidence.
3. Preserve the source brief's `meta.content_language` in review reports, next-action guidance, and any exported prompts. Current verified examples use `zh-CN` for user-facing content.
4. Record visual review availability using `references/visual-review-routing.md`.
5. Compare the result against the selected strategy, brief goals, page or app structure, `DESIGN.md`, and review checklist.
6. Separate execution issues from source-brief problems.
7. Choose the review decision.
8. Save the review artifacts.
9. Write conditionally enabled next actions: direct repair, external prompt, or revise spec. Pick exactly one `recommended_next_action`.
10. Export a prompt only when the chosen follow-up is the external-prompt path, or when a checked regression fixture intentionally exercises prompt export.

## Decision Table

| Decision | Use when | Next artifact |
|---|---|---|
| `accept` | The core goal, page or app structure, visual rules, required states, and critical checks are satisfied. Minor polish is not blocking. | Save review only. No modification prompt required. |
| `tweak` | The direction is right and the selected strategy and `DESIGN.md` remain valid. | Recommend either confirmed direct repair when editable local source exists, or an external modification prompt. |
| `revise_brief_then_regenerate` | The result failed because the source brief/spec missed or misstated necessary guidance. Preserve the selected strategy unless the review explicitly says the strategy is wrong. | Save `brief-revision.md` and update `design-spec.md` or create `design-spec-revision.md`, then point the user to the new copy source. |
| `regenerate_from_scratch` | The result ignored the page type, selected strategy, structure, or visual system enough that local edits would be slower or misleading. | Recommend a full regeneration prompt or revised spec path. |

## Required Review Outputs

Write review artifacts under the project directory:

```text
reviews/
  result-review.md
  result-review.json
  review-next-actions.md
  brief-revision.md
  design-spec-revision.md
prompts/
  <target>-modification.txt
```

`brief-revision.md` is required only for `revise_brief_then_regenerate`. `design-spec-revision.md` is required when the next usable copy source is not the existing `design-spec.md`.

Modification prompt files are not mandatory review outputs. They are generated when the user chooses the external-prompt path, or when a checked example intentionally keeps them as optional export fixtures.

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
- `design_spec_revision_path`: required for `revise_brief_then_regenerate` when the next copy source is a new spec file.
- `prompt_intent`: required for non-accepted reviews: `targeted_modification`, `brief_revision_regeneration`, or `full_regeneration`.
- `prompt.keep`, `prompt.change`, and `prompt.acceptance_checks`: required non-empty arrays for non-accepted reviews.
- `next_actions.recommended_next_action`: required for non-accepted reviews: `direct_repair`, `external_prompt`, `revise_spec`, or `regenerate_from_spec`.
- `next_actions.reason`: required text explaining the recommendation.
- `next_actions.options`: required array including `direct_repair`, `external_prompt`, and `revise_spec`; each option must include `enabled`, `disabled_reason` when disabled, and `next_copy_source` when enabled.

## Decision To Prompt Mapping

- `accept`: no `prompt_intent` or modification prompt is required.
- `tweak`: use `prompt_intent: targeted_modification`.
- `revise_brief_then_regenerate`: use `prompt_intent: brief_revision_regeneration` and include `brief_revision_path`.
- `regenerate_from_scratch`: use `prompt_intent: full_regeneration`.

Prompt intent records what prompt could be generated. It does not mean a review-only request already authorized exporting every platform prompt or editing files.

## Next Action Rules

- `direct_repair` can be enabled only for supported editable local evidence, currently local `.txt`, `.md`, `.html`, or `.json` files, and still requires explicit user confirmation before edits.
- `external_prompt` is the safe default for pasted summaries, screenshots, image-only results, Figma exports, and external-platform drafts.
- `revise_spec` is recommended when the result exposes a source brief/spec gap. It must point the user to updated `design-spec.md` or `design-spec-revision.md`.
- Non-editable evidence must disable `direct_repair` with a plain-language reason.
- Accepted reviews do not require modification prompts or repair options.

## Review State Matrix

| State | Saved files allowed | Edits allowed | Required next step |
|---|---|---|---|
| Missing source package or evidence | None beyond notes already in chat | No | Ask for missing brief package, `design-spec.md`, generated result, screenshot, or local file |
| Accepted review | `result-review.md/json` | No | Tell user the result is usable |
| Non-accepted review with editable local source | `result-review.md/json`, `review-next-actions.md` | No, until confirmation | Recommend one next action and mark direct repair as enabled only after confirmation |
| Non-accepted review without editable local source | `result-review.md/json`, `review-next-actions.md` | No | Disable direct repair and recommend external prompt or spec revision |
| Confirmation declined | Existing review artifacts only | No | Leave files untouched and offer another enabled path |
| Direct repair confirmed | Review artifacts plus modified listed files | Yes, only listed files | Verify repaired files and summarize changes |
| External prompt chosen | Review artifacts plus one prompt file | No source/result edits | Tell user which prompt to copy |
| Spec revision chosen | Review artifacts plus updated spec file | Only spec files after confirmation if editing existing files | Tell user which spec to copy |

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
