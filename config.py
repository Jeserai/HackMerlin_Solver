"""
Configuration settings for HackMerlin Solver.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Resource levels
RESOURCE_LEVELS = {
    'low': {
        'use_llm': False,
        'use_embeddings': False,
        'use_online_api': False,
        'strategy': 'concatenation'
    },
    'medium': {
        'use_llm': False,
        'use_embeddings': True,
        'use_online_api': True,
        'strategy': 'embeddings'
    },
    'high': {
        'use_llm': True,
        'use_embeddings': True,
        'use_online_api': True,
        'strategy': 'llm'
    }
}

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Model settings
OPENAI_MODEL = "gpt-3.5-turbo"
HUGGINGFACE_MODEL = "Qwen/Qwen2-0.5B-Instruct"  # Lightweight local model

# Automation settings
USE_SELENIUM = True  # Set to False for manual copy/paste mode
HEADLESS_MODE = True

# Game settings
GAME_URL = "https://hackmerlin.io/"
MAX_QUESTIONS_PER_LEVEL = 10
MAX_RETRIES_PER_LEVEL = 10

# Logging
LOG_LEVEL = "INFO"
