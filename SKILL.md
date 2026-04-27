---
name: briefpilot
description: Chinese-first design collaboration flow for AI design workflows. Use for /briefpilot, or whenever a user has a vague product/page/app design request, needs START_HERE.md, a reusable design-spec.md, Google-style DESIGN.md visual system, optional prompts for huashu-design/Claude Design/v0, review checklist, or post-generation result review with safe next actions. Prefer this skill even if the user only says they want a landing page, app page, website, UI direction, generated design review, or prompt for an AI design tool.
---

# BriefPilot

BriefPilot 用在设计生成之前，也用在生成之后。它先把用户的模糊需求整理成一个可复制的 `design-spec.md`；当用户提供下游生成结果后，再用同一套 brief 判断结果是否够好，并给出安全的下一步。

## 命令入口

当用户调用 `/briefpilot` 时，直接执行本 Skill。短命令 `/bp` 是同一流程的别名，应该读取并沿用本 Skill。升级命令 `/briefpilot-upgrade` 只负责刷新或修复已安装的 BriefPilot Skill 包。

## 核心规则

不要直接生成最终设计，除非用户明确要求。先把用户请求整理成可复用 brief，并让普通用户优先复制 `design-spec.md`。平台提示词只是可选导出，不是默认第一步。

当用户只说“评审”“看看”“检查”或类似请求时，默认只做 Review：可以保存 `result-review.md`、`result-review.json` 和 `review-next-actions.md`，但不能修改源 brief、`design-spec.md`、生成结果文件或本地代码。

## 默认语言

BriefPilot 是中文优先。公开示例、brief 内容、提示词正文、评审报告和用户可见 UI 文案默认使用简体中文。文件名、JSON keys、脚本名、命令示例、工具名、组件名和设计 token 保持英文。每个 `design-brief.json` 都要写 `meta.content_language`。

## 默认流程

1. 读取用户需求、已有项目上下文，以及已有 `DESIGN.md`。
2. 按 `references/scoring-rubric.md` 诊断需求。
3. 找出最有价值的缺失信息。
4. 标准模式问 3-7 个问题；快速模式写出明确假设。
5. 先给出三个设计策略，再选择最终方向。
6. 创建新 `DESIGN.md` 前，先从 `references/design-style-index.json` 匹配本地参考方向。
7. 生成 `START_HERE.md`、`design-spec.md`、`design-brief.md`、`design-brief.json`、必要的 `DESIGN.md` 和 `review-checklist.md`。
8. `START_HERE.md` 必须给一个首选下一步，并说明普通用户复制整个 `design-spec.md`。
9. 只有用户明确要某个平台时，才导出平台提示词：v0 用于 React/Next.js 界面代码，huashu-design 用于高保真 HTML 原型，Claude Design 用于视觉探索和多版迭代。不把 `generic` 当成首轮平台提示词。
10. 默认把输出保存到 `.briefpilot/`；用户要求可见目录时再改到指定目录。

## 生成后评审模式

当用户提供生成结果、粘贴摘要、截图描述、页面评审或本地生成文件时，使用这个模式。

1. 读取源 brief 包：`design-brief.json`、关联的 `DESIGN.md`、已选策略和 `review-checklist.md`。
2. 收集结果证据：粘贴摘要、本地 `.txt` / `.md` / `.html` / `.json` 文件、截图引用或已有视觉评审。
3. 如果 brief 包或结果证据缺失，先索要缺失材料，不要直接创建正式评审报告。
4. 判断是否有视觉评审证据；有图像能力或已有 gstack 视觉评审时使用，否则记录文本/文件 fallback。
5. 对照策略、原始 brief、`DESIGN.md` 和评审清单检查结果。
6. 选择一个决定：`accept`、`tweak`、`revise_brief_then_regenerate` 或 `regenerate_from_scratch`。
7. 保存 `result-review.md`、`result-review.json` 和必要的 `review-next-actions.md`。
8. 每个未接受的结果都要有且只有一个推荐下一步：`direct_repair`、`external_prompt` 或 `revise_spec`。不可用选项必须写明原因。
9. `direct_repair` 只有在存在可编辑本地文件、BriefPilot 已列出计划修改文件、且用户明确确认后才允许执行。截图、图片、Figma 导出、外部平台结果或纯粘贴摘要不能直接修复。
10. 如果问题来自 brief/spec 缺口，必须更新 `design-spec.md` 或创建 `design-spec-revision.md`，不要让用户继续复制过期说明。

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
- 能力边界：`references/capability-boundaries.md`
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
