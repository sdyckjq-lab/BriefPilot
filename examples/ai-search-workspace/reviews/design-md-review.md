# DESIGN.md 评审报告

模式：briefpilot_fallback

是否阻断：false

参考方向：enterprise_data_workspace

来源 SHA-256：91ec3856e75d78446680917497eef94bb5f9ff7e11436ec9d3de68a1447d2207

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
- warning [reference_direction_drift] drift_checks.data_density：工作台方向需要说明扫描密度、面板、行或元数据层级。 修复建议：补充数据密度和信息层级指导，或换成更合适的参考方向。
- info [optional_official_check] official_tool：未运行 Google 官方 DESIGN.md lint，本报告使用内置 fallback 检查。 修复建议：如需更严格检查，提供安全的 --official-command 绝对路径，或手动运行官方工具。
