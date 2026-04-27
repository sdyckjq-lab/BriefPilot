# 结果评审

## 来源包

- Brief：{{brief_path}}
- DESIGN.md: {{design_md_path}}
- 已选策略：{{selected_strategy}}
- 目标工具：{{target_tool}}

## 评审证据

- 证据类型：{{evidence_kind}}
- 证据路径或来源：{{evidence_source}}
- 摘要：{{evidence_summary}}

## 保留点

- {{strength}}

## 问题

| 严重程度 | Brief 依据 | 问题 | 证据 | 建议修改 |
|---|---|---|---|---|
| {{severity}} | {{brief_reference}} | {{issue}} | {{evidence}} | {{recommended_change}} |

## 视觉评审

- 状态：{{visual_review_status}}
- 来源：{{visual_review_source}}
- 说明：{{visual_review_notes}}

## 决定

- 决定：{{decision}}
- 策略是否保留：{{strategy_preserved}}
- 策略变化原因：{{strategy_change_reason}}
- 提示意图：{{prompt_intent}}
- 推荐下一步：{{recommended_next_action}}
- 下一步原因：{{next_action_reason}}

## 下一轮提示摘要

保留：

- {{keep_item}}

修改：

- {{change_item}}

验收检查：

- {{acceptance_check}}

## 下一步选项

| 动作 | 是否可用 | 不可用原因 | 下一步复制来源 |
|---|---:|---|---|
| direct_repair | {{direct_repair_enabled}} | {{direct_repair_disabled_reason}} | {{direct_repair_copy_source}} |
| external_prompt | {{external_prompt_enabled}} | {{external_prompt_disabled_reason}} | {{external_prompt_copy_source}} |
| revise_spec | {{revise_spec_enabled}} | {{revise_spec_disabled_reason}} | {{revise_spec_copy_source}} |
