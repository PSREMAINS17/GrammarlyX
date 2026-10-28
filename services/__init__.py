"""
Services package for GrammarlyX.
Provides OpenAI LLM orchestration, text analysis, grammar checking,
style checking, and education tutoring services.
"""

from .text_analyzer import analyze_text
from .openai_service import OpenAIService, OpenAIServiceError
from .grammar_checker import GrammarCheckerService
from .style_checker import StyleCheckerService
from .education_checker import EducationCheckerService

__all__ = [
    "analyze_text",
    "OpenAIService",
    "OpenAIServiceError",
    "GrammarCheckerService",
    "StyleCheckerService",
    "EducationCheckerService",
]
