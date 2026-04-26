# Result Review: Brief Revision

## Source Package

- Brief: `design-brief.json`
- DESIGN.md: `DESIGN.md`
- Selected strategy: Dense Research Workspace
- Target tool: generic

## Reviewed Evidence

- Evidence kind: local_file
- Evidence path: `generated-results/brief-revision-case.html`
- Summary: the local generated file includes conflicting cited sources but no disagreement explanation, freshness cue, or recovery path.

## Strengths

- The result keeps the basic answer and source layout.
- The result includes multiple source cards and a source detail area.

## Mismatches

| Severity | Brief reference | Issue | Evidence | Recommended change |
|---|---|---|---|---|
| High | Brief gap: source disagreement handling | The result presents a disputed claim as complete even though cited sources disagree. | Local HTML contains conflicting external sharing status. | Revise the brief to require explicit source disagreement explanation before regenerating. |
| Medium | Source list and detail panel | The source list does not show freshness or unresolved-conflict state. | HTML has titles and excerpts only. | Add freshness metadata and conflict status to source cards and source detail. |
| Medium | Required source states | The source recovery path does not cover outdated or conflicting sources. | No retry, request-review, or mark-unresolved path. | Extend the brief guidance to include expired, conflicting, and unresolved source recovery. |

## Visual Review

- Status: not_provided
- Notes: no visual evidence was supplied; the review used HTML content and saved brief package evidence.

## Decision

- Decision: revise_brief_then_regenerate
- Strategy preserved: true
- Prompt intent: brief_revision_regeneration
- Brief revision: `brief-revision.md`

## Next Prompt Summary

Regenerate after adding disagreement handling, freshness metadata, conflict status, and unresolved-source recovery. Preserve Dense Research Workspace and `DESIGN.md`.
