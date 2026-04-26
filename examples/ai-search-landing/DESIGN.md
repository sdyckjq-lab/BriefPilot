---
version: alpha
name: BriefSearch
description: 面向 AI 搜索产品官网的克制、可信、产品驱动视觉系统。
colors:
  background: "#F8FAFC"
  surface: "#FFFFFF"
  text: "#111827"
  muted_text: "#475569"
  border: "#D8DEE8"
  primary_action: "#2563EB"
  success: "#0F766E"
  warning: "#B45309"
  danger: "#B91C1C"
  info: "#0E7490"
typography:
  display:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: 650
    lineHeight: 1.1
  title:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.2
  heading:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.25
  body:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  lg: 12px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
components:
  button_primary:
    backgroundColor: "{colors.primary_action}"
    textColor: "#FFFFFF"
    borderColor: "{colors.primary_action}"
    rounded: "{rounded.md}"
  button_secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  product_card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.lg}"
  source_chip:
    backgroundColor: "#EFF6FF"
    textColor: "{colors.primary_action}"
    borderColor: "#BFDBFE"
    rounded: "{rounded.md}"
---

# BriefSearch DESIGN.md

## Overview

BriefSearch 应该给人克制、可信、产品驱动的感觉。页面先快速说明跨工作空间 AI 搜索能解决什么，再用真实感的带来源答案界面证明这个承诺，而不是只靠抽象口号。

## Visual Theme

整体主题是冷静的企业 SaaS 官网：浅中性背景、深色正文、克制蓝色操作色、真实答案面板和紧凑信任证明。视觉应该先显得有用，再显得漂亮；所有装饰都要服务于产品证明、转化路径或信任层级。

## Colors

使用按角色命名的颜色，而不是装饰性命名。`background` 承载页面底色，`surface` 承载卡片和产品示意面板，`text` 与 `muted_text` 建立信息层级，`border` 用于低深度分隔，`primary_action` 只用于 CTA、来源链接和可见 focus。`success` 只表达已验证或安全状态，`warning` 表达谨慎提醒，`danger` 表达注册失败或演示不可用，`info` 表达中性提示。

## Typography

`display` 只用于主标题，`title` 用于主要区块，`heading` 用于能力块，`body` 用于解释文字，`caption` 用于元信息和来源标签，`label` 用于按钮、徽标和表单标签。控制行长，避免夸张展示字体让产品显得不成熟。

## Layout

桌面端采用产品驱动的官网节奏：首屏包含核心承诺、双 CTA 和带来源答案示意，之后依次展示痛点、解决方案、工作流、集成范围、安全信任和最终 CTA。首屏必须同时回答价值、产品证明和下一步动作。移动端按标题、说明、CTA、产品界面的顺序堆叠，不能横向滚动。

## Elevation & Depth

只用轻微阴影把产品示意和关键证明面板从中性背景中托起。大多数区块用边框分隔即可。避免没有承载产品、来源、集成或信任内容的漂浮装饰面板。

## Shapes

默认使用 8px 圆角。主产品示意和大型证明面板可以使用 12px。避免过度圆角、装饰色块、泡泡感构图和大量胶囊元素。

## Components

主 CTA 状态包括 default 蓝色、hover 深蓝、pressed 紧凑阴影、disabled 弱化边框、loading 等宽加载、success 确认、error 重试提示和可见 focus ring。次 CTA 保持文字优先，包含 default、hover、pressed、disabled、loading 和 focus 状态。产品卡片要展示 empty、loading、success、error 状态。来源标签要展示 default、hover、pressed、focus、unavailable 和 selected 状态。

## Responsive Behavior

使用桌面端 >= 1024px、平板 768-1023px、移动端 <= 767px。首屏产品示意缩放时不能裁切答案文字或来源标签。移动端主 CTA 要在首屏可见，或在产品证明后立即重复一次。触控目标至少 44px，并保留清楚的 keyboard focus。

## Motion & Feedback

动效要克制且有目的：短促 hover 过渡、产品示意内的 loading shimmer、CTA loading 反馈，以及不会推动周围布局的 success/error 状态变化。尊重 reduced motion 设置，用静态状态变化替代动画。

## Content Voice

文案语气直接、可信、具体、产品驱动。优先写“从所有工作资料里找到可信答案”，不要写空泛的“释放 AI 潜能”。不要虚构客户指标、认证、集成伙伴或品牌背书。

## Do's and Don'ts

Do：展示真实产品界面、来源链接、集成范围、具体工作流、安全证明、keyboard focus、可读对比度和移动端 CTA 可见性。Don't：使用泛泛 AI 口号、过量发光、抽象渐变、虚构客户 Logo、无依据指标、隐藏来源链接，或把文字放进不可读图片。

## Reference Direction

Reference direction: `ai_product_landing_page` - AI 产品官网。

只借鉴产品证明、转化清晰度、信任层级和来源支撑的视觉证据。这只是灵感边界：do not copy 第三方品牌资产、Logo、专有字体、截图、完整配色系统或完整 `DESIGN.md` 文件。

## Agent Guidance

把 front matter tokens 当成强约束。如果缺少必要 token，从最接近的角色 token 派生，并记录假设。保留已选的“企业信任型”策略、产品驱动首屏、带来源答案示意、克制蓝色操作色、可见 focus 状态，以及不虚构证明的边界。
