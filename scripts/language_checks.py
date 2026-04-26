#!/usr/bin/env python3

MIN_BRIEF_CHINESE_CHARS = 500
MIN_BRIEF_CHINESE_RATIO = 0.25
MIN_PROMPT_CHINESE_CHARS = 500
MIN_PROMPT_CHINESE_RATIO = 0.12
MIN_REVIEW_CHINESE_CHARS = 120
MIN_REVIEW_CHINESE_RATIO = 0.25


def chinese_char_count(text):
    return sum(1 for char in text if "\u4e00" <= char <= "\u9fff")


def ascii_letter_count(text):
    return sum(1 for char in text if char.isascii() and char.isalpha())


def chinese_ratio(text):
    chinese = chinese_char_count(text)
    ascii_letters = ascii_letter_count(text)
    total = chinese + ascii_letters
    return chinese / total if total else 0


def collect_string_values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(collect_string_values(item))
        return values
    if isinstance(value, dict):
        values = []
        for item in value.values():
            values.extend(collect_string_values(item))
        return values
    return []


def is_chinese_first_text(text, min_chars, min_ratio):
    return chinese_char_count(text) >= min_chars and chinese_ratio(text) >= min_ratio


def is_chinese_first_brief(brief):
    return is_chinese_first_text(
        "\n".join(collect_string_values(brief)),
        MIN_BRIEF_CHINESE_CHARS,
        MIN_BRIEF_CHINESE_RATIO,
    )


def is_chinese_first_prompt(text):
    return is_chinese_first_text(text, MIN_PROMPT_CHINESE_CHARS, MIN_PROMPT_CHINESE_RATIO)


def collect_review_text_values(review):
    values = []
    evidence = review.get("evidence") if isinstance(review.get("evidence"), dict) else {}
    if isinstance(evidence.get("summary"), str):
        values.append(evidence["summary"])

    values.extend(collect_string_values(review.get("strengths", [])))
    if isinstance(review.get("strategy_change_reason"), str):
        values.append(review["strategy_change_reason"])

    findings = review.get("findings", [])
    if isinstance(findings, list):
        for item in findings:
            if not isinstance(item, dict):
                continue
            for field in ["brief_reference", "issue", "evidence", "recommended_change"]:
                if isinstance(item.get(field), str):
                    values.append(item[field])

    visual = review.get("visual_review") if isinstance(review.get("visual_review"), dict) else {}
    if isinstance(visual.get("notes"), str):
        values.append(visual["notes"])

    prompt = review.get("prompt") if isinstance(review.get("prompt"), dict) else {}
    for field in ["keep", "change", "do_not_change", "acceptance_checks"]:
        values.extend(collect_string_values(prompt.get(field, [])))

    return values


def is_chinese_first_review(review):
    return is_chinese_first_text(
        "\n".join(collect_review_text_values(review)),
        MIN_REVIEW_CHINESE_CHARS,
        MIN_REVIEW_CHINESE_RATIO,
    )
