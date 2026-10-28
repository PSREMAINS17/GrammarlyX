"""
Quality Scoring System for GrammarlyX.

Provides an objective, transparent, and deterministic scoring mechanism
labeled as 'AI Writing Quality Indicator'.

SCORING FORMULA DOCUMENTATION:
-------------------------------------------------------------------------------
1. Grammar Score (0 - 100):
   - Base = 100.
   - Evaluates identified grammatical, spelling, and syntactic issues normalized
     against text length (per 100 words, with a minimum floor of 20 words).
   - Weights:
       * Critical errors (e.g., subject-verb agreement, verb tense, fragments): 6.0
       * Standard errors (spelling, word usage, articles): 4.5
       * Warnings (punctuation nuances, capitalization): 2.5
   - Error Penalty = (Total Error Weight / max(word_count, 20)) * 100 * 2.5
   - Grammar Score = clamp(100 - Error Penalty, 0, 100)

2. Style Score (0 - 100):
   - Base = 100.
   - Evaluates conciseness, redundancy, clarity, passive voice, and tone fit.
   - Weights:
       * Warning (e.g. excessive passive voice, run-ons, severe wordiness): 4.0
       * Suggestion (weak wording, mild repetition, filler phrases): 2.0
   - Style Penalty = (Total Style Weight / max(word_count, 20)) * 100 * 2.0
   - Style Score = clamp(100 - Style Penalty, 0, 100)

3. Readability Score (0 - 100):
   - Derived from the standard Flesch Reading Ease score:
     FRE = 206.835 - (1.015 * ASL) - (84.6 * ASW)
     where ASL = Average Sentence Length (words/sentence)
           ASW = Average Syllables per Word
   - Clamped to the [0, 100] range.

4. Overall AI Writing Quality Indicator (0 - 100):
   - Weighted composite indicator:
     Overall = (0.50 * Grammar) + (0.30 * Style) + (0.20 * Readability)
   - If style or grammar is omitted in analysis, weights dynamically normalize.
-------------------------------------------------------------------------------
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class QualityScores:
    overall_score: int
    grammar_score: int
    style_score: int
    readability_score: int
    rating_label: str
    formula_summary: str


def clamp(val: float, low: float = 0.0, high: float = 100.0) -> int:
    """Clamp float to range and return as integer."""
    return int(max(low, min(high, round(val))))


def get_rating_label(overall_score: int) -> str:
    """Translate numerical score to a user-friendly qualitative descriptor."""
    if overall_score >= 90:
        return "Excellent — Highly Polished"
    elif overall_score >= 80:
        return "Good — Minor Improvements Suggested"
    elif overall_score >= 70:
        return "Satisfactory — Several Edits Needed"
    elif overall_score >= 55:
        return "Needs Revision — Noticeable Grammar/Style Issues"
    else:
        return "Critical Attention Required — Significant Errors Detected"


def calculate_quality_scores(
    word_count: int,
    errors: Optional[List[Dict[str, Any]]] = None,
    style_issues: Optional[List[Dict[str, Any]]] = None,
    flesch_reading_ease: Optional[float] = None,
) -> QualityScores:
    """
    Deterministically compute quality indicator scores.
    """
    effective_words = max(word_count, 20)

    # 1. Grammar Score Calculation
    grammar_score = 100
    if errors is not None:
        if len(errors) == 0:
            grammar_score = 100
        else:
            total_weight = 0.0
            for err in errors:
                severity = str(err.get("severity", "error")).lower()
                err_type = str(err.get("type", "grammar")).lower()

                if "agreement" in err_type or "tense" in err_type or "fragment" in err_type:
                    weight = 6.0
                elif severity == "warning":
                    weight = 2.5
                else:
                    weight = 4.5

                total_weight += weight

            penalty = (total_weight / effective_words) * 100.0 * 2.5
            grammar_score = clamp(100.0 - penalty)

    # 2. Style Score Calculation
    style_score = 100
    if style_issues is not None:
        if len(style_issues) == 0:
            style_score = 100
        else:
            total_style_weight = 0.0
            for item in style_issues:
                sev = str(item.get("severity", "suggestion")).lower()
                if sev == "warning":
                    total_style_weight += 4.0
                else:
                    total_style_weight += 2.0

            style_penalty = (total_style_weight / effective_words) * 100.0 * 2.0
            style_score = clamp(100.0 - style_penalty)

    # 3. Readability Score Calculation
    readability_score = 75
    if flesch_reading_ease is not None:
        readability_score = clamp(flesch_reading_ease)

    # 4. Overall Weighted Score
    has_grammar = errors is not None
    has_style = style_issues is not None

    if has_grammar and has_style:
        overall = (0.50 * grammar_score) + (0.30 * style_score) + (0.20 * readability_score)
    elif has_grammar:
        overall = (0.75 * grammar_score) + (0.25 * readability_score)
    elif has_style:
        overall = (0.70 * style_score) + (0.30 * readability_score)
    else:
        overall = readability_score

    overall_int = clamp(overall)
    label = get_rating_label(overall_int)

    formula_summary = (
        "Calculated deterministically using: "
        f"Grammar ({grammar_score}/100, 50% weight), "
        f"Style ({style_score}/100, 30% weight), and "
        f"Readability ({readability_score}/100, 20% weight)."
    )

    return QualityScores(
        overall_score=overall_int,
        grammar_score=grammar_score,
        style_score=style_score,
        readability_score=readability_score,
        rating_label=label,
        formula_summary=formula_summary,
    )
