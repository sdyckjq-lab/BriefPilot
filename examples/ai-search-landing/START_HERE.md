# 从这里开始

## 你拿到了什么

这是 BriefSearch AI 搜索产品官网的 BriefPilot 设计包。它把“帮我做一个 AI 搜索产品官网”整理成可复用的设计规范、视觉系统和评审标准。

## 先看哪个文件

核心文件是 `design-spec.md`。第一轮生成时，完整复制这个文件即可。

## 首选下一步

首选下一步：复制整个 `design-spec.md` 到 huashu-design，生成一个高保真官网 HTML 原型。

## 怎么选工具

- 想要 React / Next.js 可运行界面代码：用 v0。
- 想要高保真、可查看的 HTML 原型：用 huashu-design。
- 想要先探索官网视觉方向或做多版变化：用 Claude Design。

## 可选导出

`prompts/` 里的平台提示词是可选导出。已经明确要用某个平台时再复制对应文件；不确定时继续使用 `design-spec.md`。

## 生成后带什么回来评审

把生成出的 HTML 文件、页面摘要、截图说明或已有视觉评审带回来。只说“评审”“看看”“检查”时，BriefPilot 只保存评审报告和下一步建议，不会改 brief、`design-spec.md`、生成结果文件或本地代码。
