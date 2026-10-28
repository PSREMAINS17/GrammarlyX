"""
Input validation and sanitization utilities for GrammarlyX.
Ensures input robustness without distorting normal user writing.
"""

import re
from typing import Tuple
from config import MIN_INPUT_CHARS, MAX_INPUT_CHARS


class ValidationError(Exception):
    """Custom exception raised when text fails validation checks."""
    pass


def sanitize_input_text(text: str) -> str:
    """
    Safely normalize whitespace and remove unprintable control characters,
    preserving unicode letters, common punctuation, quotes, code symbols, and newlines.
    """
    if not text:
        return ""

    # Remove null bytes and non-printable control characters except standard tabs and newlines
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Normalize carriage returns to standard newlines
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # Avoid runs of excessive empty lines (more than 3 in a row)
    cleaned = re.sub(r"\n{4,}", "\n\n\n", cleaned)

    return cleaned.strip()


def validate_input_text(text: str) -> Tuple[bool, str]:
    """
    Validate user input text against empty input, length thresholds, and invalid formats.
    Returns (is_valid: bool, error_message: str).
    """
    if text is None:
        return False, "Input cannot be empty. Please enter or paste some text to analyze."

    stripped = text.strip()
    if len(stripped) == 0:
        return False, "Input cannot be empty. Please enter or paste some text before clicking 'Analyze Text'."

    if len(stripped) < MIN_INPUT_CHARS:
        return (
            False,
            f"Text is too short for meaningful analysis. Please provide at least {MIN_INPUT_CHARS} characters."
        )

    if len(text) > MAX_INPUT_CHARS:
        return (
            False,
            f"Input text exceeds the maximum supported length of {MAX_INPUT_CHARS:,} characters "
            f"(currently {len(text):,} characters). Please shorten your text."
        )

    # Check if text contains at least some alphanumeric characters
    if not re.search(r"[a-zA-Z0-9]", stripped):
        return (
            False,
            "The input contains only symbols or punctuation. Please provide meaningful sentences or words."
        )

    return True, ""
