---
name: bp-review
description: Review-only companion for BriefPilot. Use for /bp-review when the user brings back generated design output, a local result file, screenshot description, pasted summary, or visual review and wants the same Chinese-first result-review.md, result-review.json, review-next-actions.md, and safe follow-up guidance provided by /briefpilot. This skill delegates to the installed briefpilot result-review workflow instead of creating a separate review system.
---

# /bp-review

`/bp-review` 是 BriefPilot 的生成后评审入口。

## 执行方式

1. 找到同一 Skill 安装目录里的 `briefpilot` Skill，并读取它的 `SKILL.md`。
2. 直接进入 BriefPilot 的生成后评审模式，也就是主 Skill 里的 result-review workflow。
3. 先确认源 brief 包和结果证据是否齐全：`design-brief.json`、关联 `DESIGN.md`、已选策略、`review-checklist.md`，以及生成结果摘要、截图说明、本地文件或已有视觉评审。
4. 只保存评审产物和下一步建议：`result-review.md`、`result-review.json`、`review-next-actions.md`，必要时再生成 `brief-revision.md`、`design-spec-revision.md` 或外部修改提示词。
5. 不要在本 Skill 中复刻 BriefPilot 模板、脚本、参考资料或评审规则。

## 安全边界

如果用户只说“评审”“看看”“检查”，默认只审查，不改 brief、不改 `design-spec.md`、不改生成结果文件，也不改本地代码。

直接修本地文件必须等用户明确确认，并且先列出准备修改的文件。截图、图片、Figma 导出、外部平台草稿和纯粘贴摘要不能直接修，只能给评审、外部修改提示或修订后的 spec。

如果找不到 `briefpilot` Skill，说明安装不完整。请告诉用户重新安装 BriefPilot Skill 包，或运行 `/briefpilot-upgrade` 修复安装。
