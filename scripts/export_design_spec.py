#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def value_at(data, dotted_path, default=""):
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current if current is not None else default


def selected_strategy(brief):
    strategy = value_at(brief, "visual.strategy_name")
    if has_text(strategy):
        return strategy.strip()
    for option in brief.get("strategy_options", []):
        if isinstance(option, dict) and option.get("selected") and has_text(option.get("name")):
            return option["name"].strip()
    return ""


def as_list(value):
    if isinstance(value, list):
        return [item for item in value if has_text(item) or isinstance(item, dict)]
    if has_text(value):
        return [value]
    return []


def bullet_list(items, fallback="待补充。"):
    cleaned = [str(item).strip() for item in items if has_text(item)]
    if not cleaned:
        return [f"- {fallback}"]
    return [f"- {item}" for item in cleaned]


def section_details_lines(brief):
    details = value_at(brief, "structure.section_details", [])
    if not isinstance(details, list) or not details:
        return bullet_list(value_at(brief, "structure.sections", []), "待补充页面或界面内容清单。")

    lines = []
    for item in details:
        if not isinstance(item, dict):
            continue
        section = item.get("section", "未命名区块")
        purpose = item.get("purpose", "待补充目的")
        content = ", ".join(str(entry) for entry in as_list(item.get("content")) if has_text(entry))
        visual_anchor = item.get("visual_anchor", "")
        line = f"- {section}：{purpose}"
        if content:
            line += f" 内容包括：{content}。"
        if has_text(visual_anchor):
            line += f" 视觉锚点：{visual_anchor}。"
        lines.append(line)
    return lines or bullet_list(value_at(brief, "structure.sections", []), "待补充页面或界面内容清单。")


def first_screen_lines(brief):
    details = value_at(brief, "structure.section_details", [])
    if isinstance(details, list) and details:
        first = next((item for item in details if isinstance(item, dict)), {})
        section = first.get("section", "首屏或首要界面")
        purpose = first.get("purpose", "先让用户理解页面是什么、为什么可信、下一步做什么。")
        visual_anchor = first.get("visual_anchor", "")
        lines = [f"- {section}：{purpose}"]
        if has_text(visual_anchor):
            lines.append(f"- 首屏视觉锚点：{visual_anchor}")
    else:
        sections = as_list(value_at(brief, "structure.sections", []))
        first = sections[0] if sections else "首屏或首要界面"
        lines = [f"- {first} 必须先回答：这是什么、给谁用、用户下一步做什么。"]

    for item in as_list(value_at(brief, "structure.responsive_accessibility", [])):
        if any(keyword in item for keyword in ["首屏", "移动端", "桌面端", "来源", "可信"]):
            lines.append(f"- {item}")
    return lines


def extract_markdown_section(text, heading):
    marker = f"## {heading}"
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == marker:
            start = index + 1
            break
    if start is None:
        return ""
    collected = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def render_design_spec(brief, design_text="", design_label=None):
    project_name = value_at(brief, "project.name", "未命名项目")
    content_language = value_at(brief, "meta.content_language", "zh-CN")
    primary_user = value_at(brief, "audience.primary_user", "待补充主要用户")
    design_goal = value_at(brief, "goals.design_goal", "待补充设计目标")
    business_goal = value_at(brief, "goals.business_goal", "待补充业务目标")
    primary_cta = value_at(brief, "goals.primary_cta", "")
    secondary_cta = value_at(brief, "goals.secondary_cta", "")
    core_claim = value_at(brief, "message.core_claim", "待补充核心信息")
    strategy = selected_strategy(brief) or "待补充策略"
    design_path = design_label or value_at(brief, "design_system.design_md_path", "DESIGN.md")
    reference_direction = value_at(brief, "design_system.reference_direction.id", "")
    agent_guidance = extract_markdown_section(design_text, "Agent Guidance")
    content_voice = extract_markdown_section(design_text, "Content Voice")

    lines = [
        f"# {project_name} 设计规范",
        "",
        "## 怎么使用",
        "",
        "- 完整复制本文件到设计生成工具里，作为第一轮生成的核心说明。",
        "- 如果你不确定应该选哪个平台，先复制本文件；不要先在多个平台提示词之间来回选择。",
        "- 平台提示词只是可选导出，适合已经明确要用 v0、huashu-design 或 Claude Design 的时候。",
    ]
    if content_language == "zh-CN":
        lines.append("- 用户可见 UI 文案必须使用简体中文；文件名、JSON keys、命令、组件名和 design token keys 保持英文。")
    lines.extend(
        [
            "",
            "## 主要任务",
            "",
            f"- 项目：{project_name}",
            f"- 主要用户：{primary_user}",
            f"- 业务目标：{business_goal}",
            f"- 设计目标：{design_goal}",
            f"- 核心信息：{core_claim}",
            f"- 已选视觉策略：{strategy}",
        ]
    )
    if has_text(primary_cta):
        lines.append(f"- 主操作：{primary_cta}")
    if has_text(secondary_cta):
        lines.append(f"- 次操作：{secondary_cta}")

    lines.extend(["", "## 首屏或首要界面层级", ""])
    lines.extend(first_screen_lines(brief))

    lines.extend(["", "## 内容清单", ""])
    lines.extend(section_details_lines(brief))

    lines.extend(["", "## 交互状态和行为", ""])
    lines.extend(bullet_list(value_at(brief, "structure.interaction_states", []), "待补充状态。"))
    lines.extend(bullet_list(value_at(brief, "structure.interaction_contract", []), "待补充交互行为。"))

    lines.extend(["", "## 响应式和可访问性", ""])
    lines.extend(bullet_list(value_at(brief, "structure.responsive_accessibility", []), "待补充响应式和可访问性要求。"))
    lines.extend(bullet_list(value_at(brief, "constraints.accessibility", []), "待补充可访问性约束。"))

    lines.extend(
        [
            "",
            "## 视觉系统",
            "",
            f"- 视觉系统来源：`{design_path}`",
            f"- 策略：{strategy}",
        ]
    )
    if has_text(reference_direction):
        lines.append(f"- 参考方向：`{reference_direction}`")
    lines.extend(bullet_list(value_at(brief, "design_system.token_summary", []), "以 DESIGN.md 中的角色 token 为准。"))
    if has_text(content_voice):
        lines.extend(["", "内容语气摘录：", "", content_voice])
    if has_text(agent_guidance):
        lines.extend(["", "执行规则摘录：", "", agent_guidance])

    forbidden = [
        "不要做泛泛功能卡片；每个能力区块都必须回到本产品的用户任务、证据或操作。",
        "不要虚构客户评价、客户 Logo、指标、认证、集成伙伴或真实来源数据。",
        "不要使用模糊 CTA；主操作和次操作必须和 brief 中的目标一致。",
        "不要套用通用 dashboard card、抽象渐变、AI 发光背景或没有功能意义的装饰卡片。",
    ]
    forbidden.extend(str(item).strip() for item in as_list(value_at(brief, "visual.avoid", [])) if has_text(item))
    forbidden.extend(str(item).strip() for item in as_list(value_at(brief, "quality_bar.must_avoid", [])) if has_text(item))
    lines.extend(["", "## 禁止的通用化结果", ""])
    lines.extend(bullet_list(dict.fromkeys(forbidden).keys()))

    lines.extend(["", "## 验收检查", ""])
    lines.extend(bullet_list(value_at(brief, "quality_bar.review_criteria", []), "待补充验收标准。"))
    lines.append("")
    return "\n".join(lines)


def load_json(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SystemExit(f"cannot read brief JSON: {error}")
    if not isinstance(data, dict):
        raise SystemExit("brief JSON must be an object")
    return data


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Export a tool-agnostic BriefPilot design-spec.md.")
    parser.add_argument("--brief", required=True, type=Path, help="Path to design-brief.json.")
    parser.add_argument("--design", required=True, type=Path, help="Path to linked DESIGN.md.")
    parser.add_argument("--out", type=Path, help="Output path. Defaults to stdout.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    brief = load_json(args.brief)
    try:
        design_text = args.design.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"cannot read DESIGN.md: {error}", file=sys.stderr)
        return 1

    rendered = render_design_spec(brief, design_text, design_label=args.design.name)
    if args.out:
        try:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(rendered, encoding="utf-8")
        except OSError as error:
            print(f"cannot write design spec: {error}", file=sys.stderr)
            return 1
        print(f"wrote {args.out}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
