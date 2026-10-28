"""
OpenAI Service for GrammarlyX.
Handles client initialization, prompt dispatch with structured JSON response enforcement,
exception recovery, network resilience, and friendly error formatting.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from openai import (
    OpenAI,
    OpenAIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)
import config

logger = logging.getLogger("GrammarlyX.OpenAIService")


class OpenAIServiceError(Exception):
    """Custom exception raised when OpenAI API requests fail with a friendly message."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class OpenAIService:
    """
    Dedicated interface for querying OpenAI models with JSON schema enforcement.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", config.OPENAI_API_KEY).strip()
        self._model = model or os.getenv("OPENAI_MODEL", config.OPENAI_MODEL).strip() or "gpt-4o-mini"
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL", config.OPENAI_BASE_URL)
        if self._base_url:
            self._base_url = self._base_url.strip() or None
        self._client: Optional[OpenAI] = None

    def get_client(self) -> OpenAI:
        """
        Lazily initialize and return the authenticated OpenAI client.
        Raises OpenAIServiceError if the key is missing or is a placeholder.
        """
        if not self._api_key or self._api_key.startswith("your_") or len(self._api_key) < 10:
            raise OpenAIServiceError(
                "OpenAI API configuration is missing or invalid. "
                "Please configure a valid OPENAI_API_KEY in your .env file or environment variables."
            )

        if self._client is None:
            self._client = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=45.0,
                max_retries=2,
            )
        return self._client

    @property
    def model_name(self) -> str:
        """Return currently configured model name."""
        return self._model

    def call_json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Execute a chat completion requiring valid JSON response format.

        Args:
            system_prompt: Guiding persona and instructions
            user_prompt: User content and context
            temperature: Sampling temperature (low for consistent structural grammar analysis)

        Returns:
            Parsed Python dictionary from OpenAI JSON response.
        """
        client = self.get_client()

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
            )

            choice = response.choices[0]
            raw_content = choice.message.content

            if not raw_content:
                raise OpenAIServiceError("The AI model returned an empty response. Please retry your request.")

            # Parse JSON
            try:
                data = json.loads(raw_content)
                return data
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON parse error on raw output: {raw_content}")
                raise OpenAIServiceError(
                    f"Failed to parse structured JSON from LLM output: {str(json_err)}",
                    original_error=json_err,
                )

        except AuthenticationError as e:
            raise OpenAIServiceError(
                "Authentication failed: The provided OpenAI API key is invalid or expired. "
                "Please verify the OPENAI_API_KEY in your .env file.",
                original_error=e,
            )
        except RateLimitError as e:
            err_str = str(e).lower()
            if "credit_balance_exhausted" in err_str or "insufficient_quota" in err_str:
                raise OpenAIServiceError(
                    "Your OpenAI account has no credits remaining ($0.00 balance). "
                    "OpenAI API requires prepaid credits (min $5) at https://platform.openai.com/settings/organization/billing/ "
                    "or you can configure a free OpenAI-compatible provider like Groq.",
                    original_error=e,
                )
            raise OpenAIServiceError(
                "OpenAI rate limit or quota exceeded. Please check your OpenAI account billing balance "
                "or wait a moment before resubmitting.",
                original_error=e,
            )
        except (APITimeoutError, TimeoutError) as e:
            raise OpenAIServiceError(
                "The request to OpenAI timed out. Please check your internet connection or try a shorter text.",
                original_error=e,
            )
        except APIConnectionError as e:
            raise OpenAIServiceError(
                "Could not connect to OpenAI services. Please check your network connection and DNS settings.",
                original_error=e,
            )
        except InternalServerError as e:
            raise OpenAIServiceError(
                "OpenAI servers are currently experiencing difficulties. Please try again shortly.",
                original_error=e,
            )
        except OpenAIError as e:
            raise OpenAIServiceError(
                f"OpenAI API Error: {str(e)}",
                original_error=e,
            )
        except OpenAIServiceError:
            raise
        except Exception as e:
            raise OpenAIServiceError(
                f"An unexpected error occurred during AI analysis: {str(e)}",
                original_error=e,
            )
