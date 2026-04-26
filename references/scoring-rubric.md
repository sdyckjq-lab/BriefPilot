# Scoring Rubric

Score a design request from 0 to 100.

| Dimension | Weight | Full-credit signal |
|---|---:|---|
| Audience clarity | 15 | The brief identifies who will use or view the design. |
| Business goal | 15 | The brief says what action or outcome the design should produce. |
| Content completeness | 15 | The brief lists sections, screens, messages, or proof points. |
| Brand context | 15 | The brief includes brand tone, `DESIGN.md`, assets, colors, typography, or forbidden styles. |
| Visual direction | 10 | The brief describes a concrete visual strategy or references. |
| Interaction scope | 10 | The brief names required pages, states, flows, or interaction depth. |
| Asset availability | 10 | The brief says what real assets exist or what placeholders are allowed. |
| Constraints | 10 | The brief names platform, technical, responsive, accessibility, timeline, or compliance constraints. |

## Levels

- 0-60: Weak brief.
  - 0-30: Not ready for generation.
  - 31-60: Can generate, but output will be unstable.
- 61-80: Ready for stable generation.
- 81-100: Strong design brief.

## Diagnosis Format

```text
Brief Score: <score>/100

Level: <level>

Main gaps:
1. <gap>: <why it matters>
2. <gap>: <why it matters>
3. <gap>: <why it matters>

Recommended next step: <quick | standard | expert>
```

## Rule

Never present the score without explaining the biggest missing information and the practical risk it creates.

Do not give full credit to a dimension because one related field exists. A strong brief must have enough concrete audience, goal, content, brand, visual, interaction, asset, and constraint detail to reach 81 or higher.
