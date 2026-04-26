# DESIGN.md Quality Rules

BriefPilot's built-in checker is a portable fallback. It catches common problems without Node/npm and writes reports that make the next action clear. Google's official `@google/design.md` tool remains the stricter optional path when a user explicitly provides a safe local command.

## Severity Policy

Blocking issues fail validation:

- Missing or malformed front matter.
- Missing canonical backbone sections.
- Missing required token groups: `colors`, `typography`, `rounded`, `spacing`, and `components`.
- Broken token references such as `{colors.primary}` when the token does not exist.
- Invalid required color values.
- Direct instructions to copy another company's logo, proprietary typeface, exact brand identity, page, or app.
- Obvious direction conflicts, such as a signed-in data workspace described only as a decorative marketing hero.

Warnings do not fail validation:

- Missing optional component states.
- Missing page/data state guidance when the rest of the backbone exists.
- Weak accessibility, responsive, motion, or content voice guidance.
- Contrast concerns that can be calculated but do not break token parsing.
- Reference-direction drift that can be fixed without changing the whole brief.

Info findings are suggestions:

- Optional official-tool recommendation.
- Summary of the matched reference direction.
- Future comparison or export suggestions.

## Fallback Check Categories

- Structure and section order.
- Token backbone and token reference resolution.
- Role-based color coverage.
- Typography hierarchy.
- Component states.
- Page and data states.
- Responsive behavior.
- Accessibility.
- Motion and feedback.
- Content voice.
- Reference direction and style-index drift.
- Brand-copy risk.

## Official Tool Boundary

BriefPilot must not silently install npm packages and must not run `npx` automatically. Official Google checks can run only when the user provides an explicit safe local command path, or when the user manually runs an official command themselves.
