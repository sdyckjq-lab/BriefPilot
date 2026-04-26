# AI Search Landing Design Brief

## Project Overview

Create a product-led SaaS landing page for an AI search product that helps knowledge workers and small teams find trusted answers across scattered work documents.

## Brief Diagnosis

- Raw request: `帮我做一个 AI 搜索产品官网`
- Initial score: 42/100
- Main gaps: no audience, CTA, product proof, brand direction, or responsive constraints were provided.
- Recommended mode: quick mode with visible assumptions for the golden demo.

## Target Audience

- Primary: knowledge workers and small teams that search across scattered work documents
- Secondary: team leads evaluating productivity tools for fast-moving internal teams
- Context: visitors need to understand whether the product can search across work tools without setup friction

## Business Goal

Drive trial signup, with demo request as the secondary conversion.

## Design Goal

Make the value of cross-workspace AI search clear in the first screen while building enterprise trust.

## Core Message

Find trusted answers across every work document in seconds.

## Required Structure

| Section | Purpose | Required content | Visual anchor |
|---|---|---|---|
| Hero | Explain the product promise immediately | Headline, short copy, primary CTA, secondary CTA, product surface mock | Search answer panel with linked source documents |
| Pain | Name the cost of scattered work knowledge | Three pain points and a plain-language impact statement | Docs, chats, tickets, and drives shown as scattered sources |
| Solution | Connect AI search to concrete user actions | Cross-tool search, source-backed answers, team knowledge reuse | Three compact product capability blocks |
| Workflow | Show the path from question to trusted answer | Ask a question, review sourced answer, open source document | Three-step product flow |
| Integrations | Make search coverage practical without fake claims | Docs, chat, tickets, drives | Generic integration placeholders with labels |
| Security | Build trust before the final CTA | Permissions-aware search, admin controls, source visibility | Calm trust panel |
| CTA | Give qualified visitors a clear next step | Trial CTA, demo CTA, short reassurance line | Simple conversion band |

## Visual Direction

- Strategy: Enterprise Trust
- Tone: restrained, credible, product-led, clear, secure
- References: modern enterprise SaaS landing pages, sourced-answer product surfaces, clean trust patterns
- Differentiators: real product surface in hero, source attribution UI, security proof before final CTA

## Strategy Options

### Enterprise Trust

Selected. Best for a credible SaaS landing page where teams need trust before signup. Lead with value, prove it with a sourced-answer product surface, then cover workflow, integrations, and security.

### Search Copilot Demo

Good when the page should feel more interactive. Lead with an example question and answer, then explain why the answer is trustworthy. Risk: the page may underplay business trust.

### Founder-Led Launch

Good when the product is early and needs a sharper narrative. Lead with the pain of scattered knowledge, then introduce the product. Risk: the page may feel less mature for enterprise buyers.

## Brand Context

Brand name is BriefSearch. Use a wordmark placeholder only. No real logo, customer metrics, or customer logos are provided.

## DESIGN.md Reference

DESIGN.md

Reference direction: `ai_product_landing_page` - use product proof, conversion clarity, and trust hierarchy as mechanisms only.

## Asset List

- Available: product surface mock placeholder, integration icon placeholders
- Missing: real screenshots, customer logos, real metrics, certification badges
- Placeholders allowed: realistic product UI placeholder and generic integration icon placeholders

## Interaction Requirements

- Represent desktop and mobile landing pages.
- Primary CTA opens a trial signup form or navigates to `/signup`. It needs default, hover, focus, disabled, loading, success, and error states when implemented.
- Secondary demo CTA opens or scrolls to a product demo section. It stays visually secondary and needs default, hover, focus, and loading states when implemented.
- Product mock shows a typed question, answer, source chips, and linked documents.
- Source chips and linked documents are clickable when the target tool supports interactions; otherwise label them as visual-only proof elements.
- Integration items are non-clickable placeholders unless real integration URLs are provided.
- Failed signup or unavailable demo states keep the visitor on the page with a clear retry path.
- Show a simple visitor flow from hero value to workflow proof to trial signup.

## Responsive and Accessibility Requirements

- Use desktop >= 1024px, tablet 768-1023px, and mobile <= 767px as target layout bands.
- On mobile, stack headline, copy, CTAs, and product surface in that order.
- Keep the primary CTA visible above the fold on mobile or repeat it after the product proof.
- Product mock must resize without horizontal scrolling and keep answer text, source chips, and linked documents readable.
- Keyboard tab order follows navigation, primary CTA, secondary CTA, product source links, integrations, security proof, final CTA.
- Every interactive element has a visible focus state and at least a 44px touch target on mobile.
- Use semantic heading order and descriptive alt text for product mock, source icons, and integration placeholders.

## Constraints

Responsive web landing page. Use HTML prototype, React or Next.js compatible structure, and Tailwind-compatible tokens. Keep contrast readable and focus states clear.

## Forbidden Directions

Avoid generic AI wording, excessive glow, abstract gradient blobs, fake logos, unsupported metrics, and over-rounded novelty.

## Success Criteria

First-screen clarity, clear CTA, real product surface, no generic AI wording, mobile CTA visibility.

## Open Questions

- Which integrations are confirmed for launch?
- Are there real screenshots or customer proof points available?

## Assumptions

- The product is early but credible enough to show a realistic product surface.
- The first conversion target is trial signup, with demo as secondary.
