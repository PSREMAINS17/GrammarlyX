"""
Style prompt generator for GrammarlyX.
Formats instructions to analyze style, clarity, wordiness, tone fit, passive voice,
and conciseness, returning structured JSON.
"""

from typing import Dict, Any
from config import CONTEXT_GUIDELINES, TONE_GUIDELINES


def build_style_prompt(text: str, context: str = "General", tone: str = "Neutral") -> Dict[str, str]:
    """
    Build system and user messages for structured style and tone analysis.
    """
    context_desc = CONTEXT_GUIDELINES.get(context, CONTEXT_GUIDELINES["General"])
    tone_desc = TONE_GUIDELINES.get(tone, TONE_GUIDELINES["Neutral"])

    system_instruction = f"""You are the style, tone, and clarity engine for GrammarlyX, an expert AI writing assistant.
Your task is to analyze the text for stylistic improvements, clarity, conciseness, sentence variety, passive voice, wordiness, repetition, filler phrases, weak vocabulary, and alignment with the target context and tone.

Target Writing Context: {context} ({context_desc})
Target Writing Tone: {tone} ({tone_desc})

CONTEXT SENSITIVITY RULES:
- The exact same sentence MUST receive different suggestions depending on the target context.
  For example, in 'Academic Research', a phrase like 'The results are really good' should be improved to 'The results demonstrate significant empirical improvement'. In 'General', it should be improved to 'The results are very good' or 'The results are impressive'.
- In 'Business' context, prioritize executive brevity, removing bloated corporate throat-clearing ('Please be advised that', 'In order to').
- In 'Technical' context, preserve code symbols, parameters, and ensure unambiguous sequential instruction.
- In 'Education' context, suggest accessible, pedagogically lucid language.
- In 'Marketing' context, suggest dynamic, active, persuasive phrasing.

CATEGORIES TO DETECT:
- wordiness (verbose constructs, redundant modifiers)
- repetition (unnecessary repetition of words/phrases)
- filler_words (empty qualifiers like 'basically', 'actually', 'needless to say')
- weak_wording (vague or unassertive phrasing)
- clarity (confusing syntax or ambiguous reference)
- passive_voice (unnecessary passive voice that obscures agency, unless academically warranted)
- sentence_length (overly long, breathless sentences needing partition)
- formality_mismatch (slang in formal contexts, or archaic stiffness in casual contexts)
- poor_transitions (choppy links between clauses or ideas)
- redundancy (e.g., 'revert back', 'future plans', 'end result')
- tone_mismatch (discord with the requested '{tone}' tone)

CRITICAL RULES:
1. Do NOT force suggestions if the text is already concise, stylish, and context-appropriate. Return an empty list "style_issues": [] if no meaningful improvements are needed.
2. Never invent problems or distort the author's intended message.
3. Return ONLY valid JSON adhering strictly to the schema below.

REQUIRED JSON SCHEMA:
{{
    "detected_tone": "Casual / Formal / Neutral / Academic / Persuasive / Conversational",
    "formality_score": 45,
    "formality_level": "Informal / Neutral / Formal / Highly Formal",
    "tone_verdict": "Well Aligned / Needs Tone Adjustment",
    "tone_feedback": "Clear explanation assessing whether the tone was appropriate, whether the style was formal or informal, and how it aligns with the target.",
    "style_issues": [
        {{
            "text": "exact word or sentence snippet from the source text",
            "category": "wordiness",
            "severity": "warning",
            "suggestion": "clear, improved alternative snippet or rewrite",
            "explanation": "why this modification enhances readability, tone, or conciseness in the specified context"
        }}
    ]
}}
"""

    user_instruction = f"""Analyze the following text for style, clarity, detected tone, and formality level in the '{context}' context with a '{tone}' tone target:

\"\"\"
{text}
\"\"\"

Output strictly valid JSON matching the schema."""

    return {
        "system": system_instruction.strip(),
        "user": user_instruction.strip()
    }
