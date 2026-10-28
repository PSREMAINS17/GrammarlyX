"""
Education Checker Service for GrammarlyX.
Extracts deep grammatical lessons, principles, contrastive examples, and memory mnemonics
to serve as an intelligent pedagogical tutor for students and academic researchers.
"""

from typing import Dict, Any, List, Optional
from prompts.education_prompt import build_education_prompt
from .openai_service import OpenAIService, OpenAIServiceError


class EducationCheckerService:
    """
    Dedicated educational tutor service providing structured learning breakdowns.
    """

    def __init__(self, openai_service: Optional[OpenAIService] = None):
        self.openai_service = openai_service or OpenAIService()

    def check_education(self, text: str, context: str = "Education") -> Dict[str, Any]:
        """
        Analyze text to extract educational grammar and writing lessons.

        Args:
            text: Input user text
            context: Context (Education or Academic Research)

        Returns:
            Dict containing list of 'lessons'.
        """
        if not text or not text.strip():
            return {"lessons": []}

        prompt_data = build_education_prompt(text=text, context=context)

        response_dict = self.openai_service.call_json_completion(
            system_prompt=prompt_data["system"],
            user_prompt=prompt_data["user"],
            temperature=0.2,
        )

        return self._normalize_response(response_dict)

    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure educational lessons adhere to standard format.
        """
        raw_lessons = data.get("lessons")
        if not isinstance(raw_lessons, list):
            raw_lessons = []

        validated_lessons: List[Dict[str, Any]] = []
        for item in raw_lessons:
            if not isinstance(item, dict):
                continue

            mistake = str(item.get("mistake", "")).strip()
            correction = str(item.get("correction", "")).strip()
            category = str(item.get("category", "Grammar Rule")).strip()
            rule = str(item.get("rule", "")).strip()
            why_wrong = str(item.get("why_wrong", "")).strip()
            how_to_remember = str(item.get("how_to_remember", "")).strip()
            correct_example = str(item.get("correct_example", "")).strip()

            if not mistake and not correction:
                continue

            validated_lessons.append({
                "mistake": mistake,
                "correction": correction,
                "category": category,
                "rule": rule,
                "why_wrong": why_wrong,
                "how_to_remember": how_to_remember,
                "correct_example": correct_example,
            })

        return {"lessons": validated_lessons}
