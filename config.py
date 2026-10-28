"""
GrammarlyX Configuration Module
Loads environment variables and defines application constants, contexts, tones, and defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None

# Input Limits
MIN_INPUT_CHARS = 3
MAX_INPUT_CHARS = 25000

# Supported Writing Contexts
WRITING_CONTEXTS = [
    "Education",
    "Academic Research",
    "Business",
    "Technical",
    "Professional",
    "Marketing",
    "General",
]

# Supported Writing Tones
WRITING_TONES = [
    "Neutral",
    "Professional",
    "Academic",
    "Casual",
    "Formal",
    "Persuasive",
]

# Context-Specific Guidelines for Prompt Enrichment
CONTEXT_GUIDELINES = {
    "Education": (
        "Focus on clarity, learner-friendly language, and constructive pedagogical feedback. "
        "Explain errors thoroughly to foster grammatical competence and understanding."
    ),
    "Academic Research": (
        "Maintain scholarly rigor, precision, formal academic conventions, passive/active balance, "
        "and objective framing. Eliminate colloquialisms and unsupported superlatives."
    ),
    "Business": (
        "Prioritize executive brevity, professional tone, actionable clarity, and courteous confidence. "
        "Remove corporate jargon and redundant filler."
    ),
    "Technical": (
        "Emphasize precision, unambiguous phrasing, technical accuracy, and logical sequencing. "
        "Preserve domain terms, identifiers, parameters, and code-related notation."
    ),
    "Professional": (
        "Ensure polished, respectful, authoritative, and clear communication suitable for workplace "
        "correspondence, proposals, and official documents."
    ),
    "Marketing": (
        "Focus on engaging, persuasive, audience-centric language, dynamic cadence, and compelling clarity "
        "while eliminating clunky constructions."
    ),
    "General": (
        "Aim for natural, clean, grammatically sound, and effortlessly readable everyday writing."
    ),
}

# Tone Guidelines
TONE_GUIDELINES = {
    "Neutral": "Impartial, matter-of-fact, balanced, and direct without emotional coloration.",
    "Professional": "Polished, courteous, competent, and structured for workplace excellence.",
    "Academic": "Rigorous, analytical, evidence-oriented, and adhering to scholarly standards.",
    "Casual": "Conversational, approachable, relaxed, yet grammatically correct and coherent.",
    "Formal": "Dignified, serious, elevated vocabulary, avoiding contractions or slang.",
    "Persuasive": "Compelling, rhetorically effective, influential, and confidence-inspiring.",
}

# Curated Sample Texts for Demo Selector
DEMO_TEXTS = {
    "Education (Grammar & Agreement)": (
        "Students should understands the importance of regular practice because it help them improve. "
        "When a student do not study daily, they struggles during the final examinations."
    ),
    "Academic Research (Formality & Rigor)": (
        "The results are really good and it show that our hypothesis was totally right. "
        "We done lots of experiments and they proved that the algorithm runs very fast."
    ),
    "Business (Executive Action)": (
        "Our company have completed the project and we are looking forward to discuss the results. "
        "Please revert back at the earliest so we can finalize the decision."
    ),
    "Technical (Clarity & Precision)": (
        "The application don't works properly when the user enter invalid data into the input field. "
        "There is many exceptions that gets thrown by the backend server."
    ),
    "General (Everyday Composition)": (
        "She don't like programming because it are difficult and she have many problem with syntax. "
        "Yesterday she go to the library to found some helpful books."
    ),
}


def is_api_configured() -> bool:
    """Check if a non-placeholder OpenAI API key is set."""
    key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY).strip()
    return bool(key) and not key.startswith("your_") and len(key) > 10


def get_configured_model() -> str:
    """Return the currently configured OpenAI model."""
    return os.getenv("OPENAI_MODEL", OPENAI_MODEL).strip() or "gpt-4o-mini"
