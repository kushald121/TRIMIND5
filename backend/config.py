"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
# Try environment variable first, then no fallback (must be set by user)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Council members - list of OpenRouter model identifiers
# Using Mistral, Devstral, and GLM models
# Note: These models require sufficient API credits
COUNCIL_MODELS = [
    "mistralai/mistral-large-2407",  # Mistral Large (correct identifier)
    "mistralai/pixtral-12b-2409",    # Alternative if devstral not available
    "01-ai/yi-1.5-34b-chat",         # Alternative high-quality model
]

# Referee model - synthesizes final response  
# Using Mistral Large for synthesis
CHAIRMAN_MODEL = "mistralai/mistral-large-2407"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"