# Design Style Index

BriefPilot uses this local index before writing a new `DESIGN.md`. It is a first-version set of 12 reference directions, written by BriefPilot, and stored locally in `design-style-index.json`.

## How To Use It

1. Match the task to one or two likely directions using the request, task type, audience, and selected strategy.
2. Prefer the direction whose `primary_matching_signals` match the brief's core job.
3. If two directions both fit, use `conflict_resolution` and choose the one that best matches the first-screen job.
4. If confidence is low, use `ai_product_landing_page` for visitor-facing product pages and `enterprise_data_workspace` for signed-in product surfaces, then mark the choice as an assumption.
5. Put the chosen direction in `design-brief.json` under `design_system.reference_direction`.
6. Write the direction into `DESIGN.md` under `## Reference Direction`.
7. Run the built-in checks; they use the same index to warn when the file drifts from the chosen direction.

## Boundary

Reference mechanisms, do not copy brands.

The links in the index point to mature public design systems and selected public `DESIGN.md` collections for inspiration. BriefPilot does not fetch them at runtime, does not treat `awesome-design-md` as an official Google source, and does not copy full third-party `DESIGN.md` files, logos, fonts, screenshots, color systems, or brand identities.

Use the pattern behind a source: density, hierarchy, component states, reading flow, trust markers, or product proof. Do not copy the source's brand.

## Current Directions

- `ai_product_landing_page`
- `developer_tool`
- `enterprise_data_workspace`
- `documentation_knowledge_base`
- `finance_payments`
- `creation_tool`
- `consumer_app`
- `commerce_brand_retail`
- `media_editorial`
- `productivity_tool`
- `collaboration_workflow`
- `premium_visual_showcase`

Future work may let users import a local external `DESIGN.md` and rewrite it into a project-specific style. This phase only defines the boundary and the `reference_direction` data shape.
