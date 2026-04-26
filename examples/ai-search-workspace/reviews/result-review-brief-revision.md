# Result Review: Brief Revision

## Source Package

- Brief: `design-brief.json`
- DESIGN.md: `DESIGN.md`
- Selected strategy: 密集研究工作台
- Target tool: generic

## Reviewed Evidence

- Evidence kind: local_file
- Evidence path: `generated-results/brief-revision-case.html`
- Summary: 本地生成的 HTML 中有两个引用来源对外部分享审批是否最终完成给出冲突信息，但页面把答案呈现为完整结论，没有解释来源冲突、信息新鲜度或恢复路径。

## Strengths

- 生成文件保留了基础答案和来源布局。
- 本地结果包含多个来源卡片和来源详情区域。

## Mismatches

| Severity | Brief reference | Issue | Evidence | Recommended change |
|---|---|---|---|---|
| high | `brief gap: 没有指定来源冲突处理` | 结果把有争议的说法呈现为完整结论，但引用来源之间存在冲突。 | 本地 HTML 同时包含 Security policy v4 和 Admin memo draft，二者对外部分享状态描述冲突，但页面没有冲突说明。 | 先修订 brief，明确要求展示来源冲突说明，再重新生成。 |
| medium | `structure.section_details: 引用来源列表和来源详情面板` | 来源列表没有展示信息新鲜度或未解决冲突状态。 | 本地 HTML 有来源标题和摘录，但没有新鲜度提示或冲突状态。 | 在来源卡片和来源详情中加入新鲜度元数据和冲突状态。 |
| medium | `quality_bar.must_have: 来源不可用和权限受限状态` | 来源恢复路径没有覆盖过期或冲突来源。 | 生成结果没有为有争议证据提供重试、请求复核或标记未解决路径。 | 扩展 brief 指导，加入过期、冲突和未解决来源的恢复方式。 |

## Visual Review

- Status: not_provided
- Notes: 本地文件评审没有提供视觉证据；判断依据是 HTML 内容和已保存 brief 包。

## Decision

- Decision: revise_brief_then_regenerate
- Strategy preserved: true
- Prompt intent: brief_revision_regeneration
- Brief revision: `brief-revision.md`

## Next Prompt Summary

加入来源冲突处理、新鲜度元数据、冲突状态和未解决来源恢复路径后重新生成。保留“密集研究工作台”和 `DESIGN.md`。
