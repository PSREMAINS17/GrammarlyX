"""
Unit tests for prompts module.
Verifies prompt construction, context insertion, and schema requirements without making API calls.
"""

import pytest
from prompts.grammar_prompt import build_grammar_prompt
from prompts.style_prompt import build_style_prompt
from prompts.education_prompt import build_education_prompt


def test_grammar_prompt_structure():
    sample_text = "She don't like the new algorithm."
    res = build_grammar_prompt(sample_text, context="Academic Research", tone="Formal")

    assert "system" in res
    assert "user" in res
    assert "Academic Research" in res["system"]
    assert "Formal" in res["system"]
    assert sample_text in res["user"]
    assert "corrected_text" in res["system"]
    assert "errors" in res["system"]


def test_style_prompt_context_adaptation():
    sample_text = "The results are really good."
    res = build_style_prompt(sample_text, context="Business", tone="Professional")

    assert "Business" in res["system"]
    assert "Professional" in res["system"]
    assert sample_text in res["user"]
    assert "style_issues" in res["system"]
    assert "wordiness" in res["system"]
    assert "detected_tone" in res["system"]
    assert "formality_level" in res["system"]


def test_education_prompt_structure():
    sample_text = "He go to school yesterday."
    res = build_education_prompt(sample_text, context="Education")

    assert "lessons" in res["system"]
    assert "how_to_remember" in res["system"]
    assert "why_wrong" in res["system"]
    assert sample_text in res["user"]
