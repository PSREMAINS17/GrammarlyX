
"""
GrammarlyX Configuration Module
Loads Streamlit secrets and local environment variables.
Defines application constants, contexts, tones, and defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from local .env file
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_setting(name: str, default: str = "") -> str:
    """Read Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, None)
    except Exception:
        # Streamlit secrets may be unavailable during local development
        value = None

    if value is None or str(value).strip() == "":
        value = os.getenv(name, default)

    return str(value).strip()


# API settings: Streamlit Cloud Secrets take priority
OPENAI_API_KEY = get_setting("OPENAI_API_KEY")
OPENAI_MODEL = get_setting("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = get_setting("OPENAI_BASE_URL") or None

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

# Context-Specific Guidelines
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

# Curated Sample Texts
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
    """Check whether a valid-looking API key is configured."""
    key = get_setting("OPENAI_API_KEY")
    return bool(key) and not key.startswith("your_") and len(key) > 10


def get_configured_model() -> str:
    """Return the configured model name."""
    return get_setting("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
