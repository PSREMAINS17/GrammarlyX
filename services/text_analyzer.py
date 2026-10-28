"""
Deterministic text statistics and readability engine for GrammarlyX.
Performs pure-Python natural language measurement without external model dependencies or API calls.
"""

import re
from typing import Dict, Any, List


def count_syllables_in_word(word: str) -> int:
    """
    Estimate syllables in an English word using phonetic heuristic rules.
    """
    word = word.lower().strip()
    if not word:
        return 0

    # Remove non-alphabetic trailing characters
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 1

    # Single-letter edge case
    if len(word) <= 2:
        return 1

    # Exception rules for common silent e or endings
    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    # Adjust for silent 'e' at end
    if word.endswith("e") and not word.endswith("le") and len(word) > 2:
        if count > 1:
            count -= 1

    # Adjust for 'ed' past tense suffix
    if word.endswith("ed") and not word.endswith("ted") and not word.endswith("ded"):
        if count > 1:
            count -= 1

    # Guarantee at least 1 syllable for non-empty word
    return max(1, count)


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences while respecting common abbreviations (Mr., Dr., etc.).
    """
    if not text.strip():
        return []

    # Protect common honorifics and abbreviations
    abbreviations = [
        r"\bMr\.", r"\bMrs\.", r"\bMs\.", r"\bDr\.", r"\bProf\.",
        r"\be\.g\.", r"\bi\.e\.", r"\betc\.", r"\bvs\.", r"\bInc\.", r"\bCorp\."
    ]
    protected = text
    placeholder_map = {}
    for i, abbr_pattern in enumerate(abbreviations):
        matches = re.findall(abbr_pattern, protected, flags=re.IGNORECASE)
        for match in set(matches):
            token = f"__ABBR_{i}_{len(token) if 'token' in locals() else 0}__"
            placeholder_map[token] = match
            protected = protected.replace(match, token)

    # Split on sentence boundaries: punctuation followed by whitespace or end
    raw_sentences = re.split(r"(?<=[.!?])\s+", protected)

    sentences = []
    for s in raw_sentences:
        restored = s.strip()
        for token, original in placeholder_map.items():
            restored = restored.replace(token, original)
        if restored:
            sentences.append(restored)

    return sentences


def get_flesch_reading_grade(score: float) -> str:
    """Return qualitative grade label for a Flesch Reading Ease score."""
    if score >= 90:
        return "Very Easy (5th Grade)"
    elif score >= 80:
        return "Easy (6th Grade)"
    elif score >= 70:
        return "Fairly Easy (7th Grade)"
    elif score >= 60:
        return "Standard / Plain English (8th - 9th Grade)"
    elif score >= 50:
        return "Fairly Difficult (10th - 12th Grade)"
    elif score >= 30:
        return "Difficult (College Level)"
    else:
        return "Very Difficult (Graduate / Professional Level)"


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Perform deterministic statistical and readability analysis on input text.

    Returns:
        Dict containing word count, character count, sentence count,
        paragraph count, averages, readability metrics, and reading times.
    """
    if not text or not text.strip():
        return {
            "word_count": 0,
            "char_count": 0,
            "char_count_no_spaces": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "avg_words_per_sentence": 0.0,
            "avg_word_length": 0.0,
            "longest_sentence_words": 0,
            "longest_sentence_text": "",
            "flesch_reading_ease": 100.0,
            "flesch_kincaid_grade": 0.0,
            "readability_grade": "N/A",
            "complex_words_count": 0,
            "syllable_count": 0,
            "estimated_reading_time_mins": 0.0,
        }

    # Extract words
    words = re.findall(r"\b[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?\b", text)
    word_count = len(words)

    # Characters
    char_count = len(text)
    char_count_no_spaces = len(re.sub(r"\s", "", text))

    # Paragraphs (blocks separated by one or more newlines)
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    paragraph_count = max(1, len(paragraphs)) if word_count > 0 else 0

    # Sentences
    sentences = split_into_sentences(text)
    sentence_count = max(1, len(sentences)) if word_count > 0 else 0

    # Words per sentence and longest sentence
    longest_sentence_words = 0
    longest_sentence_text = ""
    for s in sentences:
        s_words = re.findall(r"\b[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?\b", s)
        s_count = len(s_words)
        if s_count > longest_sentence_words:
            longest_sentence_words = s_count
            longest_sentence_text = s

    avg_words_per_sentence = round(word_count / sentence_count, 1) if sentence_count > 0 else 0.0

    # Word lengths and syllables
    total_word_chars = sum(len(w) for w in words)
    avg_word_length = round(total_word_chars / word_count, 1) if word_count > 0 else 0.0

    total_syllables = sum(count_syllables_in_word(w) for w in words)
    complex_words = sum(1 for w in words if count_syllables_in_word(w) >= 3)

    # Readability: Flesch Reading Ease
    # FRE = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    if word_count > 0 and sentence_count > 0:
        asl = word_count / sentence_count
        asw = total_syllables / word_count
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = max(0.0, min(100.0, fre))

        # Flesch-Kincaid Grade Level
        # FKGL = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
        fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
        fkgl = max(0.0, round(fkgl, 1))
    else:
        fre = 100.0
        fkgl = 0.0

    fre_rounded = round(fre, 1)
    readability_label = get_flesch_reading_grade(fre_rounded)

    # Average reading speed: 200 words per minute
    reading_time = round(word_count / 200.0, 1)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_word_length": avg_word_length,
        "longest_sentence_words": longest_sentence_words,
        "longest_sentence_text": longest_sentence_text,
        "flesch_reading_ease": fre_rounded,
        "flesch_kincaid_grade": fkgl,
        "readability_grade": readability_label,
        "complex_words_count": complex_words,
        "syllable_count": total_syllables,
        "estimated_reading_time_mins": reading_time,
    }
