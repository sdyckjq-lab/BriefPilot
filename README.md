# BriefPilot

BriefPilot 把模糊的产品页、官网或应用页面需求，整理成一个好复制的 `design-spec.md`、`DESIGN.md` 视觉系统、可选的平台提示词，以及生成结果后的安全评审和下一步建议。

BriefPilot 默认中文优先。技术文件名、命令、JSON keys 和工具名保留英文。

## 为什么需要它

很多 AI 设计结果不是在生成时才坏掉，而是在输入阶段就不清楚。BriefPilot 先回答：做给谁看、为什么做、要证明什么、页面该怎么组织、视觉方向是什么、最后怎么判断结果够不够好。

## 会产出什么

- Brief Score
- 缺口诊断
- 聚焦问题或明确假设
- 三个设计策略方向
- `START_HERE.md`
- 可直接复制的 `design-spec.md`
- Markdown 版设计 brief
- JSON 版设计 brief，包含 `meta.content_language`
- Google-style DESIGN.md 视觉系统
- 内置 DESIGN.md 质量报告；用户提供安全本地命令时，可选接入 Google 官方 lint
- 面向 huashu-design、Claude Design 和 v0 的可选提示词
- 评审清单
- 生成结果评审报告
- 对未通过结果的下一步建议：直接修复、外部工具修改提示，或修订 spec 后重新生成

## 默认语言

公开示例和下游生成提示默认使用简体中文。生成提示会明确要求：用户可见 UI 文案使用简体中文；文件名、JSON keys、命令、组件名、设计 token 和工具名保持英文。

## 怎么用

安装 Skill 包后，优先用命令调用：

```text
/briefpilot 帮我做一个 AI 搜索产品官网
```

短命令等价：

```text
/bp 帮我做一个 AI 搜索产品官网
```

升级或修复安装：

```text
/briefpilot-upgrade
```

agent 会诊断需求、补充假设或提问、选择策略，并保存一套可复用资产。普通用户先打开 `START_HERE.md`，然后完整复制 `design-spec.md` 到目标设计工具。

如果已经知道目标工具，可以再导出平台提示词：

- `v0`：适合 React / Next.js 界面代码。
- `huashu-design`：适合高保真 HTML 原型。
- `Claude Design`：适合视觉探索、多版方向和迭代。

不确定时不要选提示词，直接复制 `design-spec.md`。

设计工具生成结果后，可以用同一套 brief 资产检查粘贴摘要、本地生成文件、截图说明或已有视觉评审。只说“评审”“看看”“检查”时，BriefPilot 默认只保存评审报告和下一步建议，不会改 brief、`design-spec.md`、生成结果文件或本地代码。

需要直接修本地文件时，BriefPilot 必须先列出准备修改的文件，并等用户明确确认。截图、图片、Figma 导出、外部平台草稿和纯粘贴摘要不能直接修复，只能评审、给外部工具修改提示，或修订 `design-spec.md` 后重新生成。

BriefPilot 的内置 `DESIGN.md` 检查不需要 Node/npm。Google 官方 `@google/design.md` lint 路径是 optional，并且 BriefPilot never silently installs npm packages、never automatically runs `npx`。

生成内置设计报告：

```text
python3 scripts/check_design_md.py DESIGN.md --mode fallback --markdown-out reviews/design-md-review.md --json-out reviews/design-md-review.json
```

使用已经安装好的 Google 官方本地命令：

```text
python3 scripts/check_design_md.py DESIGN.md --mode auto --official-command /absolute/path/to/design.md --markdown-out reviews/design-md-review.md --json-out reviews/design-md-review.json
```

Google 官方 `diff`、`export` 和 `spec` 命令适合手动跟进；当前 BriefPilot 版本只包装官方 `lint`。

当前已验证范围：AI 搜索 SaaS 官网黄金样例，以及 AI 搜索研究工作台 / 答案详情页的结果评审闭环。其他应用原型和复杂产品页暂时属于相邻试用范围。

## 对比演示

打开 [examples/comparison-demo/index.html](examples/comparison-demo/index.html)，可以看到同一个模糊需求的两种结果：直接生成的受控基线，以及基于已验证 AI 搜索官网样例的 BriefPilot 强化结果。

这个基线是第一个演示里的受控样例，不声称来自任何命名下游工具。

## 快速示例

输入：

```text
帮我做一个 AI 搜索产品官网
```

产出：

```text
Brief Score
缺口诊断
5 个聚焦问题或明确假设
3 个设计策略
diagnosis-and-strategies.md
assumptions.md
START_HERE.md
design-spec.md
design-brief.md
design-brief.json
DESIGN.md
review-checklist.md
可选平台提示词
```

评审闭环产出：

```text
result-review.md
result-review.json
review-next-actions.md
必要时生成 brief-revision.md
必要时生成 design-spec-revision.md
可选平台修改提示词
```

## Skill 包

仓库根目录是 BriefPilot 主 Skill 源码。当前命令包包含三个可安装 Skill：`briefpilot`、`bp` 和 `briefpilot-upgrade`。

当前版本写在 `VERSION`，更新记录写在 `CHANGELOG.md`。发布前先确认这两个文件一致，再生成安装包。

生成安装包：

```text
python3 scripts/validate_release_metadata.py
python3 scripts/validate_skill_commands.py
python3 scripts/package_briefpilot_skills.py --out-dir dist
```

给自动化或代理读取时，可以显式输出 JSON：

```text
python3 scripts/validate_release_metadata.py --format json
python3 scripts/validate_skill_commands.py --format json
python3 scripts/package_briefpilot_skills.py --dry-run --format json --out-dir <output-dir>
```

JSON 输出会包含 `ok`、`kind`、`findings` 和 `message`。打包脚本还会给出目标版本、当前安装版本、计划或实际生成的 `.skill` 文件、安装目录和是否完成安装。默认仍是普通文本输出。

生成后会得到：

```text
dist/briefpilot.skill
dist/bp.skill
dist/briefpilot-upgrade.skill
```

安装包会带上当前版本和更新记录，`/briefpilot-upgrade` 会据此说明是升级、修复、刷新，还是第一次进入版本化安装。

生成正式安装包时，源码目录必须是 BriefPilot 的 Git 仓库根目录，并且工作区必须干净。这样安装包里的提交号才和实际内容一致。

直接修复安装目录时，脚本默认不会把较新的已安装版本替换成旧版本；确实需要降级时必须显式加 `--allow-downgrade`。
