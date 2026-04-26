# Review Rubric

Use this rubric to judge downstream design outputs against the brief and `DESIGN.md`.

For saved Phase 2 result reviews, use `result-review-workflow.md` as the source of truth. This file is the short rubric used inside that workflow.

## Review Dimensions

1. Audience fit
2. Goal fit
3. Information structure
4. Brand and visual direction
5. Content quality
6. Interaction and responsiveness

## Rules

- Review the result against the chosen strategy, not against generic taste.
- Check whether the first screen makes the product or offer understandable.
- Check whether the primary action is visible and specific.
- Check whether required sections, screens, or states are present.
- Check whether CTA behavior, source links, visual-only fallbacks, loading/success/error states, and demo entry behavior are clear.
- Check whether desktop, tablet, and mobile layouts preserve the core message without horizontal scrolling.
- Check whether keyboard order, visible focus, semantic headings, alt text, and 44px mobile touch targets are covered.
- Check whether the result follows `DESIGN.md` and avoids forbidden directions.
- Prefer targeted tweak prompts when the direction is right.
- Use `revise_brief_then_regenerate` when the source brief missed necessary guidance before asking for another generation.
- Recommend `regenerate_from_scratch` only when the strategy, structure, page type, or visual system is ignored.
- Record visual-review fallback when screenshots or visual tools are unavailable; do not block text or file review.
