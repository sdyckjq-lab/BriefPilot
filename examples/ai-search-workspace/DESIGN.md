---
version: alpha
name: BriefSearch Workspace
description: Dense, trustworthy product workspace visual system for AI search answer review.
colors:
  background: "#F8FAFC"
  surface: "#FFFFFF"
  text: "#111827"
  muted_text: "#475569"
  border: "#D8DEE8"
  primary_action: "#2563EB"
  success: "#0F766E"
  warning: "#B45309"
  danger: "#B91C1C"
  info: "#0E7490"
typography:
  display:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.15
  title:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.2
  heading:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 650
    lineHeight: 1.25
  body:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.55
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  lg: 10px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  answer_panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  source_card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  confidence_badge:
    backgroundColor: "#ECFDF5"
    textColor: "{colors.success}"
    borderColor: "#A7F3D0"
    rounded: "{rounded.sm}"
  caution_badge:
    backgroundColor: "#FEF3C7"
    textColor: "{colors.warning}"
    borderColor: "#FCD34D"
    rounded: "{rounded.sm}"
---

# BriefSearch Workspace DESIGN.md

## Overview

BriefSearch Workspace should feel like a serious research surface, not a marketing page. It must help users understand the query, answer status, confidence, source origin, and recovery path at a glance.

## Visual Theme

The theme is a dense but calm enterprise data workspace: compact panels, visible status, strong source hierarchy, restrained blue interactions, semantic state color, and minimal decoration. Every visual choice should help users verify an AI answer.

## Colors

Use `background` for the app canvas, `surface` for answer and source panels, `text` for primary content, `muted_text` for metadata, and `border` for structure. Use `primary_action` for active links, citations, selected source cards, and focus. Use `success` for verified sources, `warning` for low-confidence or partial answers, `danger` for failed answer or permission errors, and `info` for neutral guidance.

## Typography

Use compact interface typography. `display` is reserved for the query or page title, `title` for answer section headers, `heading` for panel titles, `body` for answer text, `caption` for source metadata, and `label` for badges and controls. Source metadata must remain legible even when dense.

## Layout

Desktop uses a top search area, main answer column, cited source list, and right source-detail panel. Tablet collapses source detail below the source list. Mobile order is search, answer status, answer body, sources, source detail, then save/share actions. Keep query, confidence, answer, and source origin visible in the first screen on desktop.

## Elevation & Depth

Use subtle borders more than shadows. Panels should feel stable and workspace-like, with no floating decorative cards. Use elevation only for active overlays, menus, or selected-source detail.

## Shapes

Use 8px radius as the default and 10px for larger panels. Keep badges compact. Avoid pill-heavy layouts, novelty shapes, decorative blobs, and over-rounded panels.

## Components

Search input states: empty, input, submitting, failed, retry, disabled, and focus. Answer panel states: empty, generating, success, partial, low-confidence, failed, and unavailable. Source cards show default, hover, pressed, selected, focus, loading, unavailable, permission-blocked, and error states. Save/share controls show idle, working, success, failed, disabled, and focus states.

## Responsive Behavior

Use desktop >= 1024px, tablet 768-1023px, and mobile <= 767px. No horizontal scrolling on mobile. Source cards, citation markers, and save/share controls wrap cleanly. Keyboard order follows search input, submit, answer citations, source cards, source detail actions, then save/share controls. Touch targets are at least 44px on mobile.

## Motion & Feedback

Use restrained feedback: answer generation skeleton, source-card loading row, selected-source highlight, save/share progress, and retry feedback. Respect reduced motion by replacing animated loading with static progress labels. State changes must not jump the layout.

## Content Voice

Voice is clear, trustworthy, source-forward, and operational. Labels should say what happened and what to do next: "Low confidence, check sources" is better than "AI is thinking." Do not invent customer data, proprietary source names, accuracy metrics, or unsupported claims.

## Do's and Don'ts

Do show answer provenance, confidence, source citations, selected source detail, keyboard focus, touch-safe controls, low-confidence states, unavailable source states, and permission-blocked recovery. Don't use marketing-first composition, generic AI glow, abstract gradients, hidden sources, identical-looking states, fake source data, or decorative panels that compete with the answer.

## Reference Direction

Reference direction: `enterprise_data_workspace` - Enterprise data workspace.

Use this direction for data density, source hierarchy, permission states, and repeated-use ergonomics. It is an inspiration boundary only: do not copy third-party brand assets, logos, proprietary fonts, screenshots, full color systems, or complete `DESIGN.md` files.

## Agent Guidance

Treat front matter tokens as normative. If a needed token is missing, derive from the closest semantic role and record the assumption. Preserve the Dense Research Workspace strategy, source-forward hierarchy, visible low-confidence and permission states, restrained blue interactions, and no-fake-source-data boundary.
