---
name: bp
description: Short command alias for BriefPilot. Use for /bp whenever the user wants the same Chinese-first START_HERE.md, design-spec.md, DESIGN.md visual system, optional target-tool prompts, review checklist, or generated-result review workflow provided by /briefpilot. This skill should delegate to the installed briefpilot skill rather than creating a separate workflow.
---

# /bp

`/bp` 是 `/briefpilot` 的短命令。

## 执行方式

1. 找到同一 Skill 安装目录里的 `briefpilot` Skill，并读取它的 `SKILL.md`。
2. 用原始用户请求继续执行 BriefPilot 完整流程。
3. 不要在本 Skill 中复刻 BriefPilot 模板、脚本或参考资料。

如果找不到 `briefpilot` Skill，说明安装不完整。请告诉用户重新安装 BriefPilot Skill 包，或运行 `/briefpilot-upgrade` 修复安装。
