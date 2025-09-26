"""
HackMerlin Solver - An AI-powered word puzzle solver for HackMerlin game.

This package provides automated solving capabilities for the HackMerlin word puzzle game,
supporting multiple AI strategies including LLM, embeddings, and rule-based approaches.
"""

__version__ = "1.0.0"
__author__ = "HackMerlin Team"

from .core.solver import HackMerlinSolver
from .core.game_automation import GameAutomation
from .core.prompt_generator import PromptGenerator
from .core.response_parser import ResponseParser
from .core.word_matcher import WordMatcher
from .ai.resource_manager import ResourceManager
from .utils.config import *

__all__ = [
    "HackMerlinSolver",
    "GameAutomation", 
    "PromptGenerator",
    "ResponseParser",
    "WordMatcher",
    "ResourceManager"
]
