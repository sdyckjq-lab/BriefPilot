# DESIGN.md 质量证明

范围：AI 搜索产品官网黄金样例。

## 之前的轻量版本

早期 `DESIGN.md` 已经能给出基础视觉方向，例如颜色、字体、布局、组件和禁止事项。它证明文件可以被复用，但还没有充分说明状态、响应式、可访问性、动效、内容语气和参考边界。

## 升级后的版本

升级后的文件让下游提示词更容易稳定执行，具体体现在：

- 更强的 token 骨架：颜色角色覆盖背景、表面、正文、弱化文字、边框、主操作、成功、警示、危险和信息状态。
- 更清楚的字体层级：display、title、heading、body、caption 和 label 都有使用规则。
- 更完整的状态说明：CTA、产品卡片、来源标签、loading、empty、success、error、unavailable、disabled、focus、hover 和 pressed 都被明确命名。
- 更清楚的可访问性指导：键盘顺序、可见 focus、44px 触控目标、reduced motion 和可读换行都有明确要求。
- 更强的参考边界：明确使用 `ai_product_landing_page`，只借鉴产品证明和转化机制，不复制具体品牌。

## 限制

这是一份提示词就绪证明。本仓库这次没有运行外部下游设计生成工具。
