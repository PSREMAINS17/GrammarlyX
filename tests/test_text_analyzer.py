"""
Unit tests for services/text_analyzer.py.
Validates word counting, sentence parsing, syllable estimation, and Flesch readability calculations.
"""

import pytest
from services.text_analyzer import (
    analyze_text,
    count_syllables_in_word,
    split_into_sentences,
    get_flesch_reading_grade,
)


def test_empty_and_whitespace_input():
    res = analyze_text("")
    assert res["word_count"] == 0
    assert res["sentence_count"] == 0
    assert res["char_count"] == 0

    res_ws = analyze_text("   \n\t  ")
    assert res_ws["word_count"] == 0
    assert res_ws["sentence_count"] == 0


def test_basic_word_and_char_counts():
    sample = "The quick brown fox jumps over the lazy dog."
    res = analyze_text(sample)
    assert res["word_count"] == 9
    assert res["char_count"] == len(sample)
    assert res["char_count_no_spaces"] == len(sample.replace(" ", ""))
    assert res["sentence_count"] == 1
    assert res["paragraph_count"] == 1


def test_sentence_splitting_with_abbreviations():
    sample = "Dr. Smith went to the laboratory at 9 a.m. He met Prof. Jones there. Everything went smoothly."
    sentences = split_into_sentences(sample)
    assert len(sentences) == 3
    assert "Dr. Smith" in sentences[0]
    assert "Prof. Jones" in sentences[1]


def test_syllable_estimation():
    assert count_syllables_in_word("cat") == 1
    assert count_syllables_in_word("water") == 2
    assert count_syllables_in_word("education") >= 3
    assert count_syllables_in_word("university") >= 4


def test_flesch_reading_ease_computation():
    simple_text = "The cat sat on the mat. The dog ran in the sun."
    res = analyze_text(simple_text)
    assert res["flesch_reading_ease"] >= 70.0  # Simple text should have high readability score

    complex_text = (
        "Epistemological formulations substantiate idiosyncratic paradigms within socio-anthropological frameworks. "
        "Phenomenological investigations exemplify multidimensional theoretical conceptualizations."
    )
    res_complex = analyze_text(complex_text)
    assert res_complex["flesch_reading_ease"] < res["flesch_reading_ease"]


def test_longest_sentence_detection():
    sample = "Short sentence. This is a much longer sentence that contains a greater quantity of words. Another short one."
    res = analyze_text(sample)
    assert res["sentence_count"] == 3
    assert res["longest_sentence_words"] > 5
    assert "much longer sentence" in res["longest_sentence_text"]
