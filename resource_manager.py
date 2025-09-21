"""
Resource manager for HackMerlin game with configurable strategies.
"""
import logging
from typing import Optional, Dict, Any
from word_matcher import WordMatcher
from config import RESOURCE_LEVELS

logger = logging.getLogger(__name__)


class ResourceManager:
    """Resource manager that selects appropriate word matching strategy."""
    
    def __init__(self, resource_level: str = 'low'):
        self.resource_level = resource_level
        self.config = RESOURCE_LEVELS.get(resource_level, RESOURCE_LEVELS['low'])
        self.word_matcher = WordMatcher(resource_level)
        
        logger.info(f"Resource manager initialized with {resource_level} level")
        logger.info(f"Strategy: {self.config['strategy']}")
    
    def find_best_word(self, clues: Dict[str, Any]) -> Optional[str]:
        """Find the best matching word using configured strategy."""
        try:
            return self.word_matcher.find_best_match(clues)
        except Exception as e:
            logger.error(f"Error finding best word: {e}")
            return None
    
    def update_resource_level(self, new_level: str) -> None:
        """Update resource level and recreate word matcher."""
        if new_level not in RESOURCE_LEVELS:
            logger.warning(f"Invalid resource level: {new_level}")
            return
        
        self.resource_level = new_level
        self.config = RESOURCE_LEVELS[new_level]
        self.word_matcher = WordMatcher(new_level)
        
        logger.info(f"Resource level updated to: {new_level}")
        logger.info(f"New strategy: {self.config['strategy']}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
