# AI 搜索官网 Demo Evidence

## 原始输入

```text
帮我做一个 AI 搜索产品官网
```

## 运行信息

- Agent 工具：BriefPilot
- 日期：2026-05-01
- 目标：证明“模糊需求 -> 作品规范 -> 第一版 -> BriefPilot Review -> 第二版”的闭环。
- 是否人工修改：是。这个官方 demo 使用受控基线和整理后的第二版说明，用来保证对比可复现。

## 完整作品规范

- 复制源：`design-spec.md`
- 视觉系统：`DESIGN.md`
- 评审标准：`review-checklist.md`

## 第一版结果

- 文件：`first-pass/controlled-baseline.md`
- 来源：受控基线，不是命名工具输出。
- 作用：展示直接把模糊需求交给生成器时常见的弱点。

## BriefPilot Review

- 人看报告：`reviews/result-review-first-pass.md`
- 机器记录：`reviews/result-review-first-pass.json`
- 修改提示：`prompts/generic-modification.txt`
- 结论：保留“企业信任型”方向，但需要强化受众、来源证据、可信度和交互状态。

## 第二版结果

- 文件：`second-pass/briefpilot-reviewed.md`
- 来源：基于同一份 `design-spec.md` 和 BriefPilot Review 整理出的第二版结果说明。
- 作用：展示第二轮应该补上的结构、证据和验收点。

## 公开说明

这个证据包是可复现演示，不把受控基线伪装成真实平台输出。以后如果接入 v0、huashu-design、Claude Design 或其他工具的真实生成结果，必须在本文件里记录工具、日期、完整输入、是否人工修改和对应输出路径。
