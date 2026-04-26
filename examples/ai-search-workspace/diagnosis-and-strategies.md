# Diagnosis And Strategies

## Raw Input

帮我做一个 AI 搜索产品的研究工作台页面

## Brief Score

Initial score: 58

这个需求说明了产品类别和页面类型，但还没有定义答案状态、引用行为、来源详情层级和响应式规则。

## Main Gaps

- 用户角色和使用场景只是隐含，没有明确写出。
- 屏幕结构没有指定。
- 来源引用行为没有指定。
- 答案可信度、加载、失败、低可信度和部分完成状态没有指定。
- 移动端顺序和键盘行为没有指定。

## Strategy Options

### 密集研究工作台

Best use case: 分析人员和知识工作者需要快速核查带来源 AI 答案。

Visual tone: 冷静、密集、产品驱动、高信任。

Information structure focus: 桌面端同时展示搜索输入、答案状态、答案正文、来源列表和来源详情面板。

Risk: 如果信息层级不清楚，界面可能显得拥挤。

Best target tools: huashu-design, Claude Design, v0.

### 证据优先答案详情

Best use case: 产品必须先证明信任和引用质量，再强调速度。

Visual tone: 来源优先，略带编辑感，并在首屏展示证据可信度。

Information structure focus: 在次要操作之前先展示答案来源。

Risk: 可能让答案显得不够快速或不够对话式。

Best target tools: Claude Design, v0.

### 轻量团队笔记

Best use case: 页面更像团队保存的研究资料。

Visual tone: 工作区感、组织清楚、偏协作。

Information structure focus: 保存的答案、笔记、分享操作和来源详情。

Risk: 可能弱化实时搜索交互。

Best target tools: huashu-design, v0.

## Final Choice

选择“密集研究工作台”。它能让应用页面适合反复研究使用，同时证明来源可见、可信度清楚、状态完整。
