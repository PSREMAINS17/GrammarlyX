"""
Unit tests for utils/validators.py.
Validates empty input, boundary length enforcement, and sanitization behavior.
"""

import pytest
from utils.validators import validate_input_text, sanitize_input_text
from config import MIN_INPUT_CHARS, MAX_INPUT_CHARS


def test_empty_input_validation():
    is_valid, msg = validate_input_text("")
    assert not is_valid
    assert "empty" in msg.lower()

    is_valid_none, msg_none = validate_input_text(None)
    assert not is_valid_none
    assert "empty" in msg_none.lower()


def test_short_input_validation():
    is_valid, msg = validate_input_text("a")
    assert not is_valid
    assert "too short" in msg.lower()


def test_symbols_only_validation():
    is_valid, msg = validate_input_text("!@#$%^&*()_+=-{}[]:;")
    assert not is_valid
    assert "symbols" in msg.lower() or "meaningful" in msg.lower()


def test_max_length_validation():
    huge_text = "a" * (MAX_INPUT_CHARS + 50)
    is_valid, msg = validate_input_text(huge_text)
    assert not is_valid
    assert "maximum" in msg.lower()


def test_valid_input_passes():
    valid_text = "This is a legitimate English sentence that should pass input validation effortlessly."
    is_valid, msg = validate_input_text(valid_text)
    assert is_valid
    assert msg == ""


def test_sanitize_input_text():
    raw_with_control_chars = "Hello\x00World!\r\nThis is a test.\n\n\n\n\nNew paragraph."
    sanitized = sanitize_input_text(raw_with_control_chars)
    assert "\x00" not in sanitized
    assert "\r" not in sanitized
    assert "HelloWorld!" in sanitized
    assert "\n\n\n\n" not in sanitized
