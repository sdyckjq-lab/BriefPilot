# DESIGN.md 评审报告

模式：briefpilot_fallback

是否阻断：false

参考方向：ai_product_landing_page

来源 SHA-256：20b652a0287808bf8acf32aafeea73d2a536d2990b4922031971e6aedb78387e

问题数量：

- blocking: 0
- warning: 2
- info: 1

下一步：continue

官方工具：

- 可用：false
- 命令：
- 已合并：false

## 发现

- warning [missing_accessibility_guidance] Markdown body：可访问性说明缺少 touch 要求。 修复建议：补充明确的可访问性要求。
- warning [reference_direction_drift] drift_checks.product_proof：官网方向需要补充产品界面证明、截图、mock 或 demo。 修复建议：补充与所选参考方向一致的产品证明指导，或换成更合适的参考方向。
- info [optional_official_check] official_tool：未运行 Google 官方 DESIGN.md lint，本报告使用内置 fallback 检查。 修复建议：如需更严格检查，提供安全的 --official-command 绝对路径，或手动运行官方工具。
