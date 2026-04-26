# Brief Revision

## Source Review

- Review JSON: `result-review-brief-revision.json`
- Source brief: `design-brief.json`
- Selected strategy: 密集研究工作台

## Why The Brief Needs Revision

本地生成文件暴露了 brief 层面的缺口：原应用页面 brief 要求来源不可用和权限受限状态，但没有明确要求在两个引用来源互相冲突时展示冲突说明，也没有要求处理过期来源和未解决证据。

## Direction Changes

- 保留“密集研究工作台”。
- 把来源冲突处理加入必要的答案可信度行为。
- 在来源详情流程中加入来源新鲜度和未解决冲突恢复。

## Guidance To Add Before Regeneration

- 当引用来源互相冲突时，在答案和来源列表附近展示明显的冲突说明。
- 每个来源卡片在可用时展示新鲜度或最近更新时间。
- 来源详情面板要区分已确认、过期、不可用和冲突证据。
- 如果冲突尚未解释，答案区域不能把有争议说法呈现为最终结论。
- 为过期或冲突来源增加重试、请求复核或标记未解决路径。

## What Stays The Same

- 保留同一受众、应用页面工作流、来源优先的信任目标、移动端顺序和 DESIGN.md 视觉系统。

## Regeneration Notes

用这份说明创建下一轮生成提示词。除非已经保存更新后的 brief 文件，否则不要暗示完整 brief 已经被改写。
