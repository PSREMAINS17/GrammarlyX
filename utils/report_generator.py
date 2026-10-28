"""
Report generator for GrammarlyX.
Produces a comprehensive, clean, formatted plain text (.txt) report
for students, researchers, teachers, and professionals.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


def generate_text_report(
    original_text: str,
    corrected_text: str,
    context: str,
    tone: str,
    learning_mode: bool,
    model_name: str,
    scores: Any,
    stats: Dict[str, Any],
    grammar_errors: Optional[List[Dict[str, Any]]] = None,
    style_issues: Optional[List[Dict[str, Any]]] = None,
    educational_lessons: Optional[List[Dict[str, Any]]] = None,
    tone_info: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> str:
    """
    Generate an exhaustive, downloadable text report of the writing analysis.
    """
    if tone_info is None and "tone_info" in kwargs:
        tone_info = kwargs["tone_info"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    divider = "=" * 80
    subdivider = "-" * 80

    lines = [
        divider,
        "GRAMMARLYX — INTELLIGENT GRAMMAR & STYLE ANALYSIS REPORT",
        "Explain + Improve + Adapt to Context",
        divider,
        f"Generated On        : {now}",
        f"Target Context      : {context}",
        f"Target Tone         : {tone}",
        f"Learning Mode       : {'ENABLED' if learning_mode else 'DISABLED'}",
        f"Configured Model    : {model_name}",
        "",
        subdivider,
        "1. AI WRITING QUALITY INDICATOR",
        subdivider,
        f"Overall Quality Indicator : {scores.overall_score}/100 ({scores.rating_label})",
        f"  - Grammar Score         : {scores.grammar_score}/100",
        f"  - Style & Tone Score    : {scores.style_score}/100",
        f"  - Readability Score     : {scores.readability_score}/100",
        f"Scoring Basis             : {scores.formula_summary}",
        "",
        subdivider,
        "2. DETERMINISTIC TEXT STATISTICS",
        subdivider,
        f"Word Count               : {stats.get('word_count', 0)}",
        f"Character Count (total)  : {stats.get('char_count', 0)}",
        f"Characters (no spaces)   : {stats.get('char_count_no_spaces', 0)}",
        f"Sentence Count           : {stats.get('sentence_count', 0)}",
        f"Paragraph Count          : {stats.get('paragraph_count', 0)}",
        f"Avg. Words per Sentence  : {stats.get('avg_words_per_sentence', 0):.1f}",
        f"Avg. Word Length         : {stats.get('avg_word_length', 0):.1f} characters",
        f"Longest Sentence         : {stats.get('longest_sentence_words', 0)} words",
        f"Flesch Reading Ease      : {stats.get('flesch_reading_ease', 0):.1f} ({stats.get('readability_grade', 'N/A')})",
        f"Est. Reading Time        : {stats.get('estimated_reading_time_mins', 0):.1f} min",
        "",
        subdivider,
        "3. ORIGINAL TEXT",
        subdivider,
        original_text.strip(),
        "",
        subdivider,
        "4. IMPROVED / CORRECTED TEXT",
        subdivider,
        corrected_text.strip() if corrected_text else "(No corrected text generated)",
        "",
    ]

    # Grammar issues
    lines.extend([
        subdivider,
        f"5. GRAMMAR & SYNTAX ISSUES DETECTED ({len(grammar_errors or [])})",
        subdivider,
    ])

    if not grammar_errors:
        lines.append("No grammar, spelling, or punctuation errors detected! Excellent work.\n")
    else:
        for idx, err in enumerate(grammar_errors, start=1):
            lines.append(f"Issue #{idx}:")
            lines.append(f"  - Original      : \"{err.get('original', '')}\"")
            lines.append(f"  - Correction    : \"{err.get('correction', '')}\"")
            lines.append(f"  - Type          : {err.get('type', 'grammar')}")
            lines.append(f"  - Severity      : {err.get('severity', 'error').upper()}")
            lines.append(f"  - Explanation   : {err.get('explanation', '')}")
            if err.get("learning_tip"):
                lines.append(f"  - Learning Tip  : {err.get('learning_tip')}")
            lines.append("")

    # Tone and Formality Evaluation
    if tone_info:
        lines.extend([
            subdivider,
            "6. TONE & FORMALITY ASSESSMENT",
            subdivider,
            f"Detected Tone           : {tone_info.get('detected_tone', 'Neutral')} (Target: {tone})",
            f"Formality Level         : {tone_info.get('formality_level', 'Neutral')} (Score: {tone_info.get('formality_score', 50)}/100)",
            f"Tone Alignment          : {tone_info.get('tone_verdict', 'Acceptable')}",
            f"Assessment Feedback     : {tone_info.get('tone_feedback', 'N/A')}",
            "",
        ])

    # Style issues
    lines.extend([
        subdivider,
        f"7. STYLE & CONCISENESS SUGGESTIONS ({len(style_issues or [])})",
        subdivider,
    ])

    if not style_issues:
        lines.append("No style or conciseness issues detected! The text aligns with the selected context.\n")
    else:
        for idx, issue in enumerate(style_issues, start=1):
            lines.append(f"Suggestion #{idx}:")
            lines.append(f"  - Identified In : \"{issue.get('text', '')}\"")
            lines.append(f"  - Category      : {issue.get('category', 'style')}")
            lines.append(f"  - Suggestion    : \"{issue.get('suggestion', '')}\"")
            lines.append(f"  - Explanation   : {issue.get('explanation', '')}")
            lines.append("")

    # Educational lessons
    if learning_mode and educational_lessons:
        lines.extend([
            subdivider,
            f"7. EDUCATION & LEARNING BREAKDOWN ({len(educational_lessons)})",
            subdivider,
        ])
        for idx, lesson in enumerate(educational_lessons, start=1):
            lines.append(f"Lesson #{idx} — [{lesson.get('category', 'Grammar Rule')}]:")
            lines.append(f"  - Mistake         : \"{lesson.get('mistake', '')}\"")
            lines.append(f"  - Correction      : \"{lesson.get('correction', '')}\"")
            lines.append(f"  - Underlying Rule : {lesson.get('rule', '')}")
            lines.append(f"  - Why Erroneous   : {lesson.get('why_wrong', '')}")
            lines.append(f"  - How to Remember : {lesson.get('how_to_remember', '')}")
            if lesson.get("correct_example"):
                lines.append(f"  - Model Example   : {lesson.get('correct_example')}")
            lines.append("")

    lines.extend([
        divider,
        "Report compiled by GrammarlyX | Intelligent Grammar & Style Checker using LLM",
        "Confidential & Privacy-First — All analysis performed via configured OpenAI endpoint.",
        divider,
    ])

    return "\n".join(lines)
