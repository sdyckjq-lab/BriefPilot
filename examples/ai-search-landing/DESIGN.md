---
version: alpha
name: BriefSearch
description: Restrained, enterprise-trustworthy, product-led visual system for an AI search landing page.
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
    fontSize: 48px
    fontWeight: 650
    lineHeight: 1.1
  title:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.2
  heading:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.25
  body:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  lg: 12px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
components:
  button_primary:
    backgroundColor: "{colors.primary_action}"
    textColor: "#FFFFFF"
    borderColor: "{colors.primary_action}"
    rounded: "{rounded.md}"
  button_secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  product_card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.lg}"
  source_chip:
    backgroundColor: "#EFF6FF"
    textColor: "{colors.primary_action}"
    borderColor: "#BFDBFE"
    rounded: "{rounded.md}"
---

# BriefSearch DESIGN.md

## Overview

BriefSearch should feel restrained, enterprise-trustworthy, and product-led. The page must explain cross-workspace AI search quickly, then prove the claim with a realistic sourced-answer product surface.

## Visual Theme

The theme is a calm enterprise SaaS launch page: light neutral background, deep ink text, restrained blue action color, realistic answer panels, and compact trust proof. The design should feel useful before it feels decorative.

## Colors

Use role-based color, not decorative labels. `background` carries the page, `surface` carries cards and product mock panels, `text` and `muted_text` define hierarchy, `border` separates low-depth surfaces, and `primary_action` is reserved for CTA, source links, and visible focus. Use `success` only for verified or secure states, `warning` for caution, `danger` for failed signup or unavailable demo, and `info` for neutral guidance.

## Typography

Use `display` only for the main headline. Use `title` for major sections, `heading` for capability blocks, `body` for explanations, `caption` for metadata and source labels, and `label` for buttons, badges, and form labels. Keep line lengths readable and avoid dramatic display typography that makes the product feel speculative.

## Layout

Desktop uses a product-led landing rhythm: hero with claim, CTA pair, and sourced-answer mock; then pain, solution, workflow, integrations, security, and final CTA. Use consistent spacing and keep the first screen focused on value, product proof, and conversion. Mobile stacks headline, copy, CTAs, and product surface in that order without horizontal scrolling.

## Elevation & Depth

Use subtle shadows only to lift the product mock and key panels from the neutral background. Prefer borders for most section separation. Avoid floating decorative panels that do not carry product, source, integration, or trust content.

## Shapes

Use 8px radius as the default. Use 12px for the main product mock and large proof panels. Avoid over-rounded novelty shapes, decorative blobs, and pill-heavy compositions.

## Components

Primary CTA states: default blue, hover darker blue, pressed compact shadow, disabled muted border, loading spinner with unchanged width, success confirmation, error retry message, and visible focus ring. Secondary CTA stays text-forward with default, hover, pressed, disabled, loading, and focus states. Product cards show empty, loading, success, and error states. Source chips show default, hover, pressed, focus, unavailable, and selected states.

## Responsive Behavior

Use desktop >= 1024px, tablet 768-1023px, and mobile <= 767px. The hero product mock must resize without clipping answer text or source chips. Keep the primary CTA above the fold on mobile or repeat it immediately after the product proof. Maintain at least 44px touch targets and preserve visible keyboard focus.

## Motion & Feedback

Motion should be restrained and purposeful: quick hover transitions, loading shimmer inside the product mock, CTA loading feedback, and success/error state changes that do not move surrounding layout. Respect reduced motion settings by replacing animation with static state changes.

## Content Voice

Voice is direct, trustworthy, concrete, and product-led. Prefer "Find trusted answers across every work document" over vague AI claims. Do not invent customer metrics, certifications, integration partnerships, or brand claims.

## Do's and Don'ts

Do show real product surfaces, source links, integrations, specific workflow steps, security proof, keyboard focus, readable contrast, and mobile CTA visibility. Don't use generic AI slogans, excessive glow, abstract gradients, fake customer logos, unsupported metrics, hidden source links, or unreadable text in images.

## Reference Direction

Reference direction: `ai_product_landing_page` - AI product landing page.

Use this direction for product proof, conversion clarity, trust hierarchy, and source-backed visual evidence. It is an inspiration boundary only: do not copy third-party brand assets, logos, proprietary fonts, screenshots, full color systems, or complete `DESIGN.md` files.

## Agent Guidance

Treat front matter tokens as normative. If a needed token is missing, derive from the closest role token and record the assumption. Preserve the selected Enterprise Trust strategy, product-led hero, source-backed mock, restrained blue action color, visible focus states, and no-fake-proof boundary.
