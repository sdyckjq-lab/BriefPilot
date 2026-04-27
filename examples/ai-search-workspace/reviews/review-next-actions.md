# Review Next Actions

## result-review-pasted-summary.json

recommended_next_action: `external_prompt`

原因：本次证据只有粘贴摘要，没有可直接编辑的本地生成文件；最安全的下一步是复制一份外部工具修改提示。

| action | enabled | disabled_reason | next_copy_source |
|---|---:|---|---|
| direct_repair | false | 本次只提供粘贴摘要，没有可编辑本地文件路径。 |  |
| external_prompt | true |  | prompts/huashu-design-modification.txt |
| revise_spec | false | 问题主要来自生成执行偏差，原始 design-spec.md 不需要先修订。 |  |

## result-review-brief-revision.json

recommended_next_action: `revise_spec`

原因：生成结果暴露的是源 brief/spec 缺口；先复制修订后的设计规范重新生成，避免继续复制旧指导。

| action | enabled | disabled_reason | next_copy_source |
|---|---:|---|---|
| direct_repair | false | 虽然有本地 HTML 证据，但问题根源是 brief/spec 缺失，直接修 HTML 会掩盖下一轮生成风险。 |  |
| external_prompt | true |  | prompts/revised-generation.txt |
| revise_spec | true |  | reviews/design-spec-revision.md |

Review 默认只审查。只有用户确认 `direct_repair` 且 BriefPilot 已列出要编辑的文件后，才允许修改本地文件。
