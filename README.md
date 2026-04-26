# BriefPilot

BriefPilot turns vague product or landing page design requests into structured, reusable design briefs, `DESIGN.md` visual systems, prompts for Claude Design, huashu-design, and v0, and post-generation review prompts.

## Why

AI design output often fails before generation starts: the input is unclear. BriefPilot sits upstream of design generators and helps define what should be made, for whom, why it matters, what style direction fits, and how the result should be judged.

## What It Produces

- Brief Score
- Gap diagnosis
- Focused questions or explicit assumptions
- Three design strategy options
- Markdown design brief
- JSON design brief
- Google-style DESIGN.md visual system
- Built-in DESIGN.md quality report, with optional Google official lint when the user provides a safe local command
- Prompts for huashu-design, Claude Design, and v0
- Review checklist
- Result review report
- Modification or regeneration prompt for non-accepted results

## Default Output

BriefPilot writes reusable project assets under `.briefpilot/` by default. Users can choose a visible directory such as `design-briefs/`.

## How to Use

Point a Skill-capable agent at `SKILL.md`, then give it a vague design request. The agent should diagnose the request, make assumptions or ask questions, choose a strategy, and save the reusable brief package before sending work to a design generator.

After a design tool produces a result, use the same saved brief package to review pasted summaries or local generated files, then export a next prompt when changes are needed.

BriefPilot's built-in `DESIGN.md` checks run without Node/npm. Google's official `@google/design.md` lint path is optional and stricter, but BriefPilot never silently installs npm packages and never automatically runs `npx`.

To write a built-in design report:

```text
python3 scripts/check_design_md.py DESIGN.md --mode fallback --markdown-out reviews/design-md-review.md --json-out reviews/design-md-review.json
```

To opt into Google's stricter local lint path, provide an already-installed absolute command path:

```text
python3 scripts/check_design_md.py DESIGN.md --mode auto --official-command /absolute/path/to/design.md --markdown-out reviews/design-md-review.md --json-out reviews/design-md-review.json
```

Google's official `diff`, `export`, and `spec` commands are useful manual follow-ups, but this BriefPilot version only wraps official `lint`.

Current verified scope: the AI search SaaS landing page golden demo, plus the AI search research workspace / answer detail review loop. Other app prototypes and complex product pages remain adjacent trial scope.

## Comparison Demo

Open [examples/comparison-demo/index.html](examples/comparison-demo/index.html) to see the same vague request compared two ways: a controlled direct-generation baseline and a BriefPilot-enhanced result grounded in the verified AI search landing package.

The baseline is authored for this first demo. It is not claimed as output from a named downstream tool.

## Quick Example

Input:

```text
帮我做一个 AI 搜索产品官网
```

Output:

```text
Brief Score
Gap diagnosis
5 focused questions or visible assumptions
3 design strategies
diagnosis-and-strategies.md
assumptions.md
design-brief.md
design-brief.json
DESIGN.md
target prompts
review-checklist.md
```

Review loop output:

```text
result-review.md
result-review.json
brief-revision.md when needed
target modification prompts
```

## Skill Package

The repository root is the Skill package.

Use `SKILL.md` before sending work to a design generator.
