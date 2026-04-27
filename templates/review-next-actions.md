# Review Next Actions

## reviewed_report

`{{result_review_json}}`

## recommended_next_action

`{{recommended_next_action}}`

原因：{{reason}}

## options

| action | enabled | disabled_reason | next_copy_source |
|---|---:|---|---|
| direct_repair | {{direct_repair_enabled}} | {{direct_repair_disabled_reason}} | {{direct_repair_copy_source}} |
| external_prompt | {{external_prompt_enabled}} | {{external_prompt_disabled_reason}} | {{external_prompt_copy_source}} |
| revise_spec | {{revise_spec_enabled}} | {{revise_spec_disabled_reason}} | {{revise_spec_copy_source}} |

Review 默认只审查。只有用户确认 `direct_repair` 且 BriefPilot 已列出要编辑的文件后，才允许修改本地文件。
