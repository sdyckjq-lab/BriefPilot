---
name: briefpilot-upgrade
description: Upgrade, repair, or package an installed BriefPilot Skill command bundle. Use for /briefpilot-upgrade when the user wants to update BriefPilot, fix missing /briefpilot or /bp commands, regenerate .skill install artifacts, or validate that the briefpilot, bp, and briefpilot-upgrade skills are installed together.
---

# /briefpilot-upgrade

升级或修复 BriefPilot Skill 包。目标是让 `/briefpilot`、`/bp` 和 `/briefpilot-upgrade` 三个命令同时可用。

## 默认流程

1. 确认用户要升级或修复 BriefPilot，而不是生成设计 brief。
2. 找到完整源码目录：优先使用用户提供的本地 BriefPilot 仓库；否则读取已安装 `briefpilot` 目录里的 `install-manifest.json`，并使用其中的 `source_remote`；如果 manifest 缺失，再使用官方仓库 `https://github.com/sdyckjq-lab/BriefPilot.git` 获取临时副本。
3. 不要把已安装的 `briefpilot` 目录直接当作源码，除非它包含 `companions/`、`evals/`、`.gitignore` 和两个命令包脚本，并且通过源码校验。已安装主 Skill 通常只包含运行资源，不是完整源码。
4. 在完整源码目录先运行命令包校验。
5. 生成新的 `.skill` 安装包。
6. 如果目标 Skill 目录可写，再修复或刷新已安装的三个 Skill；否则只交付 `.skill` 文件。
7. 最后验证三个命令都存在，并用简单中文汇报结果。

## 安全规则

- 先校验源码，再替换任何已安装文件。
- 使用临时目录获取或准备新版本，不能从不完整源码直接覆盖安装。
- 不要复制 `AGENTS.md`、`docs/`、`.git/`、缓存目录或本地工作区文件。
- 不要删除用户的 `.briefpilot/` 输出资产。
- 如果目标目录不可写，生成 `.skill` 文件并告诉用户手动安装。

## 推荐命令

在 BriefPilot 完整源码目录中运行：

```text
python3 scripts/validate_skill_commands.py
python3 scripts/package_briefpilot_skills.py --out-dir dist
```

需要修复某个 Skill 目录时，先在临时目录验证，再使用：

```text
python3 scripts/package_briefpilot_skills.py --install-dir <skills-dir> --out-dir dist
```
