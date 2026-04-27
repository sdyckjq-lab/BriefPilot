# Capability Boundaries

BriefPilot can review many kinds of generated design results, but it cannot safely edit every artifact. Use this file before promising direct repair.

## Direct Repair After Confirmation

Direct repair is allowed only after BriefPilot has inspected editable local files, listed the exact files it plans to edit, and received explicit user confirmation.

The deterministic review validator currently supports local `.txt`, `.md`, `.html`, and `.json` evidence files. These formats can be reviewed and may be eligible for direct repair if the file is the source the user wants changed.

Direct repair is still an agent workflow, not a Python script guarantee. After editing, run the relevant validation command or inspect the output before reporting completion.

## Review Only

These inputs can be reviewed but are not directly editable by BriefPilot:

- screenshots,
- image-only mockups,
- screenshot descriptions,
- rendered pages without editable local source,
- pasted summaries,
- already-provided visual review reports.

For these, save review artifacts and recommend an external prompt or spec revision.

## External-Tool Prompt Only

These should go back to the external design tool unless the user also provides editable local source:

- Figma source designs or exports,
- external platform drafts,
- image-only design files,
- generated results that live only inside a hosted design tool.

## Confirmation Rule

The word "review" does not authorize edits. Phrases like "看看", "检查", "帮我评审一下" mean review-only.

Before local repair, BriefPilot must say which files it will edit and wait for explicit approval. Broad instructions like "帮我改好" do not bypass this step.
