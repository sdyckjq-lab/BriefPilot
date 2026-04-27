# 结果评审：Brief 修订

## 来源包

- Brief：`design-brief.json`
- DESIGN.md：`DESIGN.md`
- 已选策略：密集研究工作台
- 目标工具：generic

## 评审证据

- 证据类型：local_file
- 证据路径：`generated-results/brief-revision-case.html`
- 摘要：本地生成的 HTML 中有两个引用来源对外部分享审批是否最终完成给出冲突信息，但页面把答案呈现为完整结论，没有解释来源冲突、信息新鲜度或恢复路径。

## 保留点

- 生成文件保留了基础答案和来源布局。
- 本地结果包含多个来源卡片和来源详情区域。

## 问题

| 严重程度 | Brief 依据 | 问题 | 证据 | 建议修改 |
|---|---|---|---|---|
| high | `brief gap: 没有指定来源冲突处理` | 结果把有争议的说法呈现为完整结论，但引用来源之间存在冲突。 | 本地 HTML 同时包含 Security policy v4 和 Admin memo draft，二者对外部分享状态描述冲突，但页面没有冲突说明。 | 先修订 brief，明确要求展示来源冲突说明，再重新生成。 |
| medium | `structure.section_details: 引用来源列表和来源详情面板` | 来源列表没有展示信息新鲜度或未解决冲突状态。 | 本地 HTML 有来源标题和摘录，但没有新鲜度提示或冲突状态。 | 在来源卡片和来源详情中加入新鲜度元数据和冲突状态。 |
| medium | `quality_bar.must_have: 来源不可用和权限受限状态` | 来源恢复路径没有覆盖过期或冲突来源。 | 生成结果没有为有争议证据提供重试、请求复核或标记未解决路径。 | 扩展 brief 指导，加入过期、冲突和未解决来源的恢复方式。 |

## 视觉评审

- 状态：not_provided
- 说明：本地文件评审没有提供视觉证据；判断依据是 HTML 内容和已保存 brief 包。

## 决定

- 决定：revise_brief_then_regenerate
- 策略是否保留：true
- 提示意图：brief_revision_regeneration
- Brief 修订：`brief-revision.md`
- 推荐下一步：revise_spec
- 下一步原因：生成结果暴露的是源 brief/spec 缺口；先复制修订后的设计规范重新生成，避免继续复制旧指导。

## 下一轮提示摘要

加入来源冲突处理、新鲜度元数据、冲突状态和未解决来源恢复路径后重新生成。保留“密集研究工作台”和 `DESIGN.md`。

## 下一步选项

| 动作 | 是否可用 | 不可用原因 | 下一步复制来源 |
|---|---:|---|---|
| direct_repair | false | 虽然有本地 HTML 证据，但问题根源是 brief/spec 缺失，直接修 HTML 会掩盖下一轮生成风险。 |  |
| external_prompt | true |  | `prompts/revised-generation.txt` |
| revise_spec | true |  | `reviews/design-spec-revision.md` |
