# Visual Review Routing

Visual review is useful but optional. Lack of image support or gstack support must not block text or file review.

## Routing Ladder

1. Use direct image-reading when the current model can inspect the supplied screenshot or image.
2. Use an already-provided gstack visual review result when the user or environment supplies one.
3. Fall back to text, local file, or pasted summary review when visual evidence is not available.

## Status Values

Record visual evidence with one status:

- `available_model_image`: the current model inspected supplied visual evidence.
- `available_gstack`: an already-provided gstack visual review result was used.
- `not_provided`: no visual evidence was supplied.
- `unavailable`: visual evidence was supplied or needed, but the current environment could not inspect it.

## Rules

- `available_model_image` and `available_gstack` require a source.
- `gstack_report` evidence requires `available_gstack`.
- `screenshot_reference` evidence requires a screenshot source and either `available_model_image` or a clear `unavailable` fallback note.
- `not_provided` cannot be used for screenshot or gstack evidence.
- BriefPilot records existing visual evidence. It does not open pages, capture screenshots, install gstack, or call gstack in this phase.
