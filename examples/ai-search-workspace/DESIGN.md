---
version: alpha
name: BriefSearch Workspace
description: 面向 AI 搜索答案审查的密集、可信、产品工作台视觉系统。
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
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.15
  title:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.2
  heading:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 650
    lineHeight: 1.25
  body:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.55
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  lg: 10px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  answer_panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  source_card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  confidence_badge:
    backgroundColor: "#ECFDF5"
    textColor: "{colors.success}"
    borderColor: "#A7F3D0"
    rounded: "{rounded.sm}"
  caution_badge:
    backgroundColor: "#FEF3C7"
    textColor: "{colors.warning}"
    borderColor: "#FCD34D"
    rounded: "{rounded.sm}"
---

# BriefSearch Workspace DESIGN.md

## Overview

BriefSearch Workspace 应该像严肃的研究工作台，而不是营销页。界面必须让用户一眼看清查询、答案状态、可信度、来源出处和恢复路径，帮助他们判断 AI 答案是否能被使用。

## Visual Theme

主题是密集但冷静的企业数据工作台：紧凑面板、可见状态、强来源层级、克制蓝色交互、语义化状态颜色和极少装饰。每个视觉选择都要服务于核查 AI 答案，而不是制造气氛。

## Colors

`background` 用于应用画布，`surface` 用于答案和来源面板，`text` 用于主内容，`muted_text` 用于元信息，`border` 用于结构分隔。`primary_action` 用于活动链接、引用标记、选中来源卡片和 focus。`success` 表示已验证来源，`warning` 表示低可信度或部分完成答案，`danger` 表示答案失败或权限错误，`info` 表示中性引导。

## Typography

使用紧凑的界面字体。`display` 用于查询或页面标题，`title` 用于答案区标题，`heading` 用于面板标题，`body` 用于答案正文，`caption` 用于来源元信息，`label` 用于徽标和控件。即使信息密度高，来源元信息也必须保持可读。

## Layout

桌面端使用顶部搜索区、主答案列、引用来源列表和右侧来源详情面板。平板端把来源详情折叠到来源列表下方。移动端顺序是搜索、答案状态、答案正文、来源、来源详情，然后是保存/分享操作。桌面端首屏要同时保留查询、可信度、答案和来源出处。

## Elevation & Depth

多用细边框，少用阴影。面板应稳定、工作台化，不使用漂浮装饰卡片。只有活动浮层、菜单或选中来源详情可以使用更明显的层级。

## Shapes

默认使用 8px 圆角，大面板可使用 10px。徽标保持紧凑。避免大量胶囊形、特殊异形、装饰色块和过度圆角面板。

## Components

搜索输入状态包括 empty、input、submitting、failed、retry、disabled 和 focus。答案面板状态包括 empty、generating、success、partial、low-confidence、failed 和 unavailable。来源卡片要展示 default、hover、pressed、selected、focus、loading、unavailable、permission-blocked 和 error 状态。保存/分享控件要展示 idle、working、success、failed、disabled 和 focus 状态。

## Responsive Behavior

使用桌面端 >= 1024px、平板 768-1023px、移动端 <= 767px。移动端不能横向滚动。来源卡片、引用标记和保存/分享控件要自然换行。键盘顺序依次经过搜索输入、提交、答案引用、来源卡片、来源详情操作，再到保存/分享控件。移动端触控目标至少 44px。

## Motion & Feedback

反馈要克制：答案生成 skeleton、来源卡片 loading 行、选中来源高亮、保存/分享进度和 retry 反馈。尊重 reduced motion，用静态进度标签替代动画加载。状态变化不能让布局跳动。

## Content Voice

文案语气清楚、可信、来源优先、偏操作场景。标签要说明发生了什么以及下一步怎么做，比如“低可信度，请先核查来源”优于“AI 正在思考”。不要虚构客户数据、专有来源名称、准确率指标或无依据承诺。

## Do's and Don'ts

Do：展示答案出处、可信度、来源引用、选中来源详情、keyboard focus、适合触控的控件、低可信度状态、来源不可用状态和权限受限恢复。Don't：使用营销优先构图、泛化 AI 发光、抽象渐变、隐藏来源、看起来完全一样的状态、虚构来源数据，或用装饰面板抢走答案注意力。

## Reference Direction

Reference direction: `enterprise_data_workspace` - 企业数据工作台。

只借鉴数据密度、来源层级、权限状态和高频使用的人机工效。这只是灵感边界：do not copy 第三方品牌资产、Logo、专有字体、截图、完整配色系统或完整 `DESIGN.md` 文件。

## Agent Guidance

把 front matter tokens 当成强约束。如果缺少必要 token，从最接近的语义角色派生，并记录假设。保留“密集研究工作台”策略、来源优先层级、可见的低可信度和权限状态、克制蓝色交互，以及不虚构来源数据的边界。
