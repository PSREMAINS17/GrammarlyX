"""
Prompts package for GrammarlyX LLM generation.
"""

from .grammar_prompt import build_grammar_prompt
from .style_prompt import build_style_prompt
from .education_prompt import build_education_prompt

__all__ = [
    "build_grammar_prompt",
    "build_style_prompt",
    "build_education_prompt",
]
