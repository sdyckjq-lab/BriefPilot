---
name: briefpilot-upgrade
description: Upgrade, repair, or package an installed BriefPilot Skill command bundle. Use for /briefpilot-upgrade when the user wants to update BriefPilot, fix missing /briefpilot, /bp, or /bp-review commands, regenerate .skill install artifacts, or validate that the briefpilot, bp, bp-review, and briefpilot-upgrade skills are installed together.
---

# /briefpilot-upgrade

升级或修复 BriefPilot Skill 包。目标是让 `/briefpilot`、`/bp`、`/bp-review` 和 `/briefpilot-upgrade` 四个命令同时可用。

## 默认流程

1. 确认用户要升级或修复 BriefPilot，而不是生成设计 brief。
2. 读取已安装的 `briefpilot`、`bp`、`bp-review`、`briefpilot-upgrade` 目录里的 `install-manifest.json`。manifest 只是线索，不是可信事实。
3. 判断当前状态：
   - 四个 manifest 都存在，并且 `package_version`、`source_remote`、`source_commit` 一致，才算可比较安装。
   - manifest 缺失、没有 `package_version`，或旧包没有 `VERSION`，要说成“当前版本未知 / 未纳入版本管理”，这是第一次进入版本化升级，不要说成普通升级或精确修复。
   - `source_remote` 只有等于 `https://github.com/sdyckjq-lab/BriefPilot.git` 时，才能自动使用官方来源；非官方来源或四个命令来源不一致时，停止自动修复，要求用户提供本地完整源码或明确确认来源。
4. 找到完整源码目录：优先使用用户提供的本地 BriefPilot 仓库；否则在来源可信时使用官方仓库；同版本修复优先使用 manifest 里的完整 40 位 `source_commit` 固定来源。没有固定来源时，只能作为刷新或升级处理，先读取源码 `VERSION` 再决定。
5. 不要把已安装的 `briefpilot` 目录直接当作源码，除非它包含 `companions/`、`evals/`、`.gitignore` 和命令包脚本，并且通过源码校验。已安装主 Skill 通常只包含运行资源，不是完整源码。
6. 在完整源码目录先运行 release metadata 校验和命令包校验。
   - 源码目录必须是 BriefPilot 的 Git 仓库根目录，不能是另一个仓库里的子目录。
   - 正式打包前工作区必须干净，不能把未提交内容写进带提交号的安装包。
7. 读取源码 `VERSION`，用四段数字比较当前版本和目标版本：`0.10.0.0` 大于 `0.2.0.0`，`0.1.0.10` 大于 `0.1.0.2`。
8. 向用户说明这次操作属于升级、同版本修复、刷新、第一次版本化安装，还是需要人工确认的降级。不要自动降级；只有用户明确要求时，才可以在打包命令里使用 `--allow-downgrade`。
9. 从源码 `CHANGELOG.md` 展示目标版本的简短变更摘要；如果不能可靠摘要，就指出安装包里的 `CHANGELOG.md` 路径。
10. 生成新的 `.skill` 安装包。
11. 如果目标 Skill 目录可写，再修复或刷新已安装的四个 Skill；否则只交付 `.skill` 文件。
12. 最后验证四个命令都存在，并用简单中文汇报结果，包含当前版本、目标版本和变更摘要。

## 安全规则

- 先校验源码，再替换任何已安装文件。
- 先把已安装 manifest 当作不可信输入；只有官方 HTTPS 来源和一致的命令集元数据可以自动使用。
- 使用临时目录获取或准备新版本，不能从不完整源码直接覆盖安装。
- 不要复制 `AGENTS.md`、`docs/`、`.git/`、缓存目录或本地工作区文件。
- 不要删除用户的 `.briefpilot/` 输出资产。
- 如果目标目录不可写，生成 `.skill` 文件并告诉用户手动安装。
- 不要自动使用非官方来源；不要自动降级；不要把来源不明的同版本操作说成精确修复。

## 推荐命令

在 BriefPilot 完整源码目录中运行：

```text
python3 scripts/validate_release_metadata.py
python3 scripts/validate_skill_commands.py
python3 scripts/package_briefpilot_skills.py --out-dir dist
```

如果需要让代理或脚本读取结果，显式加 JSON 输出：

```text
python3 scripts/validate_release_metadata.py --format json
python3 scripts/validate_skill_commands.py --format json
python3 scripts/package_briefpilot_skills.py --dry-run --format json --out-dir <output-dir>
```

JSON 里的 `ok` 表示成功或失败，`findings` 列出失败原因。打包脚本还会报告目标版本、当前安装版本、计划产物、实际产物、安装目录和是否完成安装。

需要修复某个 Skill 目录时，先在临时目录验证，再使用：

```text
python3 scripts/package_briefpilot_skills.py --install-dir <skills-dir> --out-dir dist
```
