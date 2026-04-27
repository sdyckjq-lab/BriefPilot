# CHANGELOG

BriefPilot 版本记录使用 `MAJOR.MINOR.PATCH.MICRO`。

每条记录按 `YYYY-MM-DD` 标注，并优先说明用户能获得什么。

## [0.1.0.0] - 2026-04-27
### Added
- 首个明确版本的 BriefPilot Skill 包，包含 `/briefpilot`、`/bp` 和 `/briefpilot-upgrade` 三个入口。
- 支持把模糊页面需求整理成设计 brief、`DESIGN.md`、三类目标提示词和评审清单。
- 支持生成结果评审闭环，并能按评审结论导出修改或重生成提示。
- 支持内置 `DESIGN.md` 质量检查；没有 Node/npm 时也能完成基础验证。
- 发布和打包相关脚本支持显式 JSON 输出，方便代理和自动化读取结果。

### Changed
- 命令包现在保留版本和更新记录，方便升级或修复时说明当前包来自哪一版。
- 打包和校验现在要求可验证的 Git 来源，并会用可解析错误报告处理损坏的源码文件或安装记录。
