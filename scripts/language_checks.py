#!/usr/bin/env python3

MIN_BRIEF_CHINESE_CHARS = 500
MIN_BRIEF_CHINESE_RATIO = 0.25
MIN_PROMPT_CHINESE_CHARS = 500
MIN_PROMPT_CHINESE_RATIO = 0.12


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
