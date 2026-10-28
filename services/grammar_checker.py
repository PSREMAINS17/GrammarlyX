"""
Grammar Checker Service for GrammarlyX.
Orchestrates prompt construction, OpenAI inference, schema validation,
and normalization for grammatical and mechanical errors.
"""

from typing import Dict, Any, List, Optional
from prompts.grammar_prompt import build_grammar_prompt
from .openai_service import OpenAIService, OpenAIServiceError


class GrammarCheckerService:
    """
    Dedicated service for grammar, spelling, punctuation, and syntax verification.
    """

    def __init__(self, openai_service: Optional[OpenAIService] = None):
        self.openai_service = openai_service or OpenAIService()

    def check_grammar(
        self,
        text: str,
        context: str = "General",
        tone: str = "Neutral",
    ) -> Dict[str, Any]:
        """
        Analyze text for grammar and spelling errors.

        Args:
            text: Input user text
            context: Selected writing context (Education, Business, etc.)
            tone: Selected writing tone (Professional, Academic, etc.)

        Returns:
            Dict containing 'corrected_text' and list of 'errors'.
        """
        if not text or not text.strip():
            return {
                "corrected_text": text,
                "errors": []
            }

        prompt_data = build_grammar_prompt(text=text, context=context, tone=tone)

        response_dict = self.openai_service.call_json_completion(
            system_prompt=prompt_data["system"],
            user_prompt=prompt_data["user"],
            temperature=0.1,  # Low temperature for strict, reproducible corrections
        )

        return self._normalize_response(text, response_dict)

    def _normalize_response(self, original_text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure the returned structure strictly adheres to GrammarlyX contract.
        """
        corrected_text = data.get("corrected_text")
        if not corrected_text or not isinstance(corrected_text, str):
            corrected_text = original_text

        raw_errors = data.get("errors")
        if not isinstance(raw_errors, list):
            raw_errors = []

        validated_errors: List[Dict[str, Any]] = []
        for item in raw_errors:
            if not isinstance(item, dict):
                continue

            original = str(item.get("original", "")).strip()
            correction = str(item.get("correction", "")).strip()
            err_type = str(item.get("type", "grammar")).strip()
            severity = str(item.get("severity", "error")).strip().lower()
            explanation = str(item.get("explanation", "")).strip()
            learning_tip = str(item.get("learning_tip", "")).strip()

            if not original and not correction:
                continue

            if severity not in ["error", "warning"]:
                severity = "error"

            validated_errors.append({
                "original": original,
                "correction": correction,
                "type": err_type,
                "severity": severity,
                "explanation": explanation or f"Replace '{original}' with '{correction}'.",
                "learning_tip": learning_tip,
            })

        return {
            "corrected_text": corrected_text,
            "errors": validated_errors,
        }
