# AI Search Workspace Answer Detail

## Project Overview

Create an app-page workflow for an AI search product where a user asks a question, reviews a sourced answer, inspects citations, and saves or shares the result.

This is a product workspace screen, not a marketing page.

内容语言：面向用户的 UI 文案使用简体中文 (`zh-CN`)；技术标识保持英文。

## Brief Diagnosis

Initial score: 58.

Main gaps resolved by assumptions:

- Answer states were unspecified.
- Source citation behavior was unspecified.
- Source detail hierarchy was unspecified.
- Save/share behavior was unspecified.
- Mobile order and keyboard behavior were unspecified.

## Target Audience

Primary user: knowledge workers and analysts who need to verify AI search answers before using them.

Secondary user: team leads reviewing saved research artifacts from teammates.

## Business Goal

Increase trust and repeat use of sourced AI answers.

## Design Goal

Make the query, answer confidence, answer body, and source origin clear in the first screen.

## Core Message

Review every AI answer with visible sources, confidence, and recovery paths.

## Required Structure

- Top search area
- Answer status strip
- Answer body
- Cited source list
- Source detail panel
- Save/share controls

Desktop should show a top search area, a main answer-and-citations area, and a right source detail panel. Tablet can collapse source detail below the source list. Mobile should order content as search, answer status, answer body, sources, source detail, then save/share actions.

## Visual Direction

Selected strategy: Dense Research Workspace.

Tone: dense, trustworthy, calm, product-led, source-forward.

The screen should feel like a serious research surface. It should show answer provenance, confidence, source citations, and source-detail interaction without feeling cluttered.

## Strategy Options

1. Dense Research Workspace: selected. Best when analysts need to inspect a sourced AI answer quickly.
2. Evidence-First Answer Detail: source-forward, best when trust proof must come before speed.
3. Lightweight Team Notebook: organized and collaborative, best for saved team research.

## Brand Context

Brand: BriefSearch.

Use deep ink, slate, restrained blue, muted success green, and amber caution. Do not invent real customer data or proprietary source names.

## DESIGN.md Reference

Use `DESIGN.md` from this package as the source of truth for colors, type, spacing, radius, panels, source cards, and forbidden visual directions.

Reference direction: `enterprise_data_workspace` - use data density, source hierarchy, permission states, and repeated-use ergonomics as mechanisms only.

## Asset List

- `input.txt`
- `diagnosis-and-strategies.md`
- `assumptions.md`
- `design-brief.md`
- `design-brief.json`
- `DESIGN.md`
- `review-checklist.md`
- `prompts/huashu-design.txt`
- `prompts/claude-design.txt`
- `prompts/v0.txt`

## Interaction Requirements

- Search input states: empty, input, submitting, failed, retry.
- Answer area states: empty, generating, success, partial, low-confidence, failed.
- Source list states: empty, loading, available, source-unavailable.
- Source detail states: unselected, loading, success, permission-blocked.
- Save/share states: idle, working, success, failed.
- Citation markers in the answer should focus the matching source card.
- Selecting a source should update source detail without losing answer context.

## Constraints

- Responsive app-page UI.
- HTML prototype or React/Next.js-compatible structure.
- Tailwind-compatible tokens are acceptable.
- Keep realistic placeholders; do not invent customer proof.

## Forbidden Directions

- Marketing-first composition.
- Hidden or low-contrast sources.
- Generic AI glow.
- Abstract gradients.
- State changes that look identical.
- Fake source or customer proof.

## Success Criteria

- First screen shows query, trust, and source origin.
- Answer and sources have clear hierarchy.
- Source detail is discoverable.
- All required states are represented.
- Mobile order keeps answer and source context intact.
- `DESIGN.md` visual rules are followed.

## Open Questions

- Which source systems are real at launch?
- How should permission requests be routed inside the product?

## Assumptions

- The app user is already signed in.
- The product has permission-aware source access.
- The answer may be generated from multiple internal sources.
