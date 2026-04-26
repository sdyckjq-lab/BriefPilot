# Result Review: Pasted Summary

## Source Package

- Brief: `design-brief.json`
- DESIGN.md: `DESIGN.md`
- Selected strategy: Dense Research Workspace
- Target tool: generic

## Reviewed Evidence

- Evidence kind: pasted_summary
- Summary: the generated page has the right search input, answer panel, confidence badge, and save/share actions, but source cards are too quiet and citation-to-source connection is weak.

## Strengths

- The result keeps the research workspace direction.
- The answer panel, confidence badge, and save/share controls are present.

## Mismatches

| Severity | Brief reference | Issue | Evidence | Recommended change |
|---|---|---|---|---|
| Medium | `quality_bar.review_criteria` | Source cards are too low-contrast compared with the answer body. | Pasted summary says source cards are visually quiet. | Increase source card hierarchy with clearer title weight, excerpt contrast, active source state, and visible source count. |
| Medium | `structure.interaction_contract` | Citation markers do not clearly connect to source cards. | Pasted summary says citation markers are hard to connect to sources. | Make citation markers and matching source cards share an active state and visible focus treatment. |
| Low | `DESIGN.md Components` | The selected source detail panel does not clearly show active selection. | Pasted summary says selection is unclear. | Add selected-source label, active card highlight, and source metadata in the detail panel. |

## Visual Review

- Status: unavailable
- Notes: no inspectable screenshot was available; the review used pasted summary and saved brief package evidence.

## Decision

- Decision: tweak
- Strategy preserved: true
- Prompt intent: targeted_modification

## Next Prompt Summary

Keep the Dense Research Workspace strategy and DESIGN.md visual system. Strengthen source visibility, citation-to-source connection, and selected-source feedback.
