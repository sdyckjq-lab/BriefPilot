# DESIGN.md 质量证明

范围：AI 搜索研究工作台答案详情评审样例。

## 之前的轻量版本

早期 `DESIGN.md` 描述了密集、可信的工作台，并列出了关键组件。但它没有充分定义 token 角色、状态模型、响应式顺序、动效反馈、内容语气和参考方向检查，下游工具很难稳定生成可靠的应用页面。

## 升级后的版本

升级后的文件让下游提示词更容易稳定执行，具体体现在：

- 更强的 token 骨架：颜色角色覆盖答案区域、来源面板、主操作、成功、警示、危险和信息状态。
- 更清楚的字体层级：display、title、heading、body、caption 和 label 映射到查询、答案、面板标题、元数据和控件。
- 更完整的状态说明：搜索、答案面板、来源卡片、来源详情、保存/分享、loading、empty、success、partial、low-confidence、failed、unavailable 和 permission-blocked 都被明确命名。
- 更清楚的可访问性指导：键盘顺序、可见 focus、44px 触控目标、reduced motion、可读换行和语义标签都有明确要求。
- 更强的参考边界：明确使用 `enterprise_data_workspace`，只借鉴数据密度和权限状态机制，不复制具体品牌。

## 限制

这是一份提示词就绪证明。本仓库这次没有运行外部下游设计生成工具。
