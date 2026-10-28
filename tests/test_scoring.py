"""
Unit tests for utils/scoring.py.
Validates deterministic scoring algorithm, penalty weights, and boundary clamping.
"""

import pytest
from utils.scoring import calculate_quality_scores, clamp, get_rating_label


def test_clamp_function():
    assert clamp(150.0) == 100
    assert clamp(-20.0) == 0
    assert clamp(85.4) == 85
    assert clamp(85.6) == 86


def test_perfect_scores_when_no_issues():
    scores = calculate_quality_scores(
        word_count=50,
        errors=[],
        style_issues=[],
        flesch_reading_ease=85.0,
    )
    assert scores.grammar_score == 100
    assert scores.style_score == 100
    assert scores.readability_score == 85
    assert scores.overall_score >= 90
    assert "Excellent" in scores.rating_label


def test_penalties_decrease_score():
    errors = [
        {"type": "subject-verb agreement", "severity": "error"},
        {"type": "verb tense", "severity": "error"},
        {"type": "spelling", "severity": "error"},
    ]
    style_issues = [
        {"category": "wordiness", "severity": "warning"},
        {"category": "passive_voice", "severity": "suggestion"},
    ]

    scores = calculate_quality_scores(
        word_count=30,
        errors=errors,
        style_issues=style_issues,
        flesch_reading_ease=50.0,
    )

    assert scores.grammar_score < 100
    assert scores.style_score < 100
    assert scores.overall_score < 100
    assert 0 <= scores.overall_score <= 100


def test_rating_labels():
    assert "Excellent" in get_rating_label(95)
    assert "Good" in get_rating_label(82)
    assert "Satisfactory" in get_rating_label(72)
    assert "Needs Revision" in get_rating_label(58)
    assert "Critical" in get_rating_label(40)
