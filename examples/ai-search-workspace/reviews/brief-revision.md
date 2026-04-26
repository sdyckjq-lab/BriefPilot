# Brief Revision

## Source Review

- Review JSON: `result-review-brief-revision.json`
- Source brief: `design-brief.json`
- Selected strategy: Dense Research Workspace

## Why The Brief Needs Revision

The generated local file revealed a brief-level gap: the original app-page brief required source-unavailable and permission-blocked states, but it did not explicitly require source disagreement handling, outdated source recovery, or conflict explanation when two cited sources disagree.

## Direction Changes

- Preserve Dense Research Workspace.
- Add disagreement handling as a required answer trust behavior.
- Add source freshness and unresolved-conflict recovery to the source detail flow.

## Guidance To Add Before Regeneration

- When cited sources conflict, show a visible disagreement explanation near the answer and source list.
- Each source card should show freshness or last-updated metadata when available.
- The source detail panel should distinguish confirmed, stale, unavailable, and conflicting evidence.
- The answer area should avoid presenting a disputed claim as final unless the conflict is explained.
- Add a retry, request-review, or mark-unresolved path for expired or conflicting sources.

## What Stays The Same

- Keep the same audience, app-page workflow, source-forward trust goal, mobile order, and DESIGN.md visual system.

## Regeneration Notes

Use this note to create the next generation prompt. Do not imply that the full brief has been rewritten unless the updated brief files are actually saved.
