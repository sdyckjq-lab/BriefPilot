---
name: briefpilot
description: Chinese-first design brief compiler and result-review loop for AI design workflows. Use for /briefpilot, or whenever a user has a vague product/page/app design request, needs a reusable design brief, Google-style DESIGN.md visual system, prompts for huashu-design/Claude Design/v0, review checklist, or post-generation result review and modification prompts. Prefer this skill even if the user only says they want a landing page, app page, website, UI direction, generated design review, or prompt for an AI design tool.
---

# BriefPilot

BriefPilot 用在设计生成之前，也用在生成之后。它先把用户的模糊需求整理成可复用的 brief；当用户提供下游生成结果后，再用同一套 brief 判断结果是否够好，并产出下一轮修改提示。

## 命令入口

当用户调用 `/briefpilot` 时，直接执行本 Skill。短命令 `/bp` 是同一流程的别名，应该读取并沿用本 Skill。升级命令 `/briefpilot-upgrade` 只负责刷新或修复已安装的 BriefPilot Skill 包。

## 核心规则

不要直接生成最终设计，除非用户明确要求。先把用户请求整理成可复用 brief。下游工具生成结果后，先对照保存好的 brief 包做评审，再写修改提示。

## 默认语言

BriefPilot 是中文优先。公开示例、brief 内容、提示词正文、评审报告和用户可见 UI 文案默认使用简体中文。文件名、JSON keys、脚本名、命令示例、工具名、组件名和设计 token 保持英文。每个 `design-brief.json` 都要写 `meta.content_language`。

## 默认流程

1. 读取用户需求、已有项目上下文，以及已有 `DESIGN.md`。
2. 按 `references/scoring-rubric.md` 诊断需求。
3. 找出最有价值的缺失信息。
4. 标准模式问 3-7 个问题；快速模式写出明确假设。
5. 先给出三个设计策略，再选择最终方向。
6. 创建新 `DESIGN.md` 前，先从 `references/design-style-index.json` 匹配本地参考方向。
7. 生成 `design-brief.md`、`design-brief.json`、必要的 `DESIGN.md`、目标提示词和 `review-checklist.md`。
8. 默认把输出保存到 `.briefpilot/`；用户要求可见目录时再改到指定目录。

## 生成后评审模式

当用户提供生成结果、粘贴摘要、截图描述、页面评审或本地生成文件时，使用这个模式。

1. 读取源 brief 包：`design-brief.json`、关联的 `DESIGN.md`、已选策略和 `review-checklist.md`。
2. 收集结果证据：粘贴摘要、本地 `.txt` / `.md` / `.html` / `.json` 文件、截图引用或已有视觉评审。
3. 如果 brief 包或结果证据缺失，先索要缺失材料，不要直接创建正式评审报告。
4. 判断是否有视觉评审证据；有图像能力或已有 gstack 视觉评审时使用，否则记录文本/文件 fallback。
5. 对照策略、原始 brief、`DESIGN.md` 和评审清单检查结果。
6. 选择一个决定：`accept`、`tweak`、`revise_brief_then_regenerate` 或 `regenerate_from_scratch`。
7. 保存 `result-review.md` 和 `result-review.json`。每个未接受的结果都要同时保存可直接使用的修改或重生成提示。

## 已验证范围

已验证样例：

- AI 搜索 SaaS 官网黄金样例。
- AI 搜索研究工作台 / 答案详情页评审闭环。

其他 SaaS 官网、应用页面、仪表盘、幻灯片、社媒视觉或创意任务，除非已经有匹配样例，否则标记为相邻试用范围。

## 模式

- 快速模式：跳过提问，写出明确假设，确认后生成输出。
- 标准模式：问 3-7 个聚焦问题，策略确认后生成输出。
- 专家模式：高风险设计任务问 8-12 个聚焦问题。

## 资源

- 完整流程：`references/workflow.md`
- 生成后评审：`references/result-review-workflow.md`
- 视觉评审记录：`references/visual-review-routing.md`
- 资产布局：`references/asset-layout.md`
- 读取或创建 `DESIGN.md`：`references/design-md.md`
- 选择参考方向：`references/design-style-index.md`
- 判断 `DESIGN.md` 质量：`references/design-md-quality-rules.md`
- 创建 `design-brief.json`：`references/brief-schema.md`
- 评分：`references/scoring-rubric.md`
- 提问：`references/question-bank.md`
- 导出目标提示词前，读取对应 adapter reference。
- 输出结构优先复用 `templates/`。
- 需要确定性校验或导出时，优先使用 `scripts/`。
