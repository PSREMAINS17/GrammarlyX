"""
Style Checker Service for GrammarlyX.
Orchestrates prompt construction, OpenAI inference, schema validation,
and normalization for clarity, wordiness, passive voice, and context-adapted style.
"""

from typing import Dict, Any, List, Optional
from prompts.style_prompt import build_style_prompt
from .openai_service import OpenAIService, OpenAIServiceError


class StyleCheckerService:
    """
    Dedicated service for style, conciseness, passive voice, and tone optimization.
    """

    def __init__(self, openai_service: Optional[OpenAIService] = None):
        self.openai_service = openai_service or OpenAIService()

    def check_style(
        self,
        text: str,
        context: str = "General",
        tone: str = "Neutral",
    ) -> Dict[str, Any]:
        """
        Analyze text for stylistic, clarity, and tone issues.

        Args:
            text: Input user text
            context: Selected writing context (Education, Business, Academic Research, etc.)
            tone: Selected writing tone (Professional, Casual, etc.)

        Returns:
            Dict containing list of 'style_issues'.
        """
        if not text or not text.strip():
            return {"style_issues": []}

        prompt_data = build_style_prompt(text=text, context=context, tone=tone)

        response_dict = self.openai_service.call_json_completion(
            system_prompt=prompt_data["system"],
            user_prompt=prompt_data["user"],
            temperature=0.3,  # Controlled temperature for stylistic alternatives
        )

        return self._normalize_response(response_dict)

    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure style response data adheres strictly to the schema including tone and formality.
        """
        detected_tone = str(data.get("detected_tone", "Neutral")).strip() or "Neutral"
        formality_level = str(data.get("formality_level", "Neutral")).strip() or "Neutral"
        tone_verdict = str(data.get("tone_verdict", "Acceptable")).strip() or "Acceptable"
        tone_feedback = str(data.get("tone_feedback", "")).strip()

        try:
            formality_score = int(data.get("formality_score", 50))
            formality_score = max(0, min(100, formality_score))
        except (ValueError, TypeError):
            formality_score = 50

        raw_issues = data.get("style_issues")
        if not isinstance(raw_issues, list):
            raw_issues = []

        validated_issues: List[Dict[str, Any]] = []
        for item in raw_issues:
            if not isinstance(item, dict):
                continue

            text_snippet = str(item.get("text", "")).strip()
            category = str(item.get("category", "style")).strip()
            severity = str(item.get("severity", "warning")).strip().lower()
            suggestion = str(item.get("suggestion", "")).strip()
            explanation = str(item.get("explanation", "")).strip()

            if not text_snippet and not suggestion:
                continue

            if severity not in ["warning", "suggestion"]:
                severity = "warning"

            validated_issues.append({
                "text": text_snippet,
                "category": category,
                "severity": severity,
                "suggestion": suggestion,
                "explanation": explanation or f"Consider revising to: '{suggestion}'.",
            })

        return {
            "detected_tone": detected_tone,
            "formality_score": formality_score,
            "formality_level": formality_level,
            "tone_verdict": tone_verdict,
            "tone_feedback": tone_feedback or f"Tone detected as {detected_tone} with a {formality_level} formality level.",
            "style_issues": validated_issues,
        }
