"""
Prompt generator for asking Merlin strategic questions to extract individual letters.
"""
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Generates strategic prompts to ask Merlin for individual letters."""
    
    def __init__(self):
        self.asked_questions = set()
        self.current_strategy = "initial"
        
    def get_next_prompt(self, clues: Dict[str, Any] = None) -> str:
        """Get the next strategic prompt to ask Merlin."""
        try:
            if not clues:
                return "How many letters?"
            
            return self._get_strategic_prompt(clues)
                
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return "How many letters?"
    
    def _get_strategic_prompt(self, clues: Dict[str, Any]) -> str:
        """Generate strategic prompts to extract all individual letters."""
        letter_count = clues.get('letter_count')
        
        # Step 1: Get letter count
        if not letter_count:
            return "How many letters?"
        
        # Step 2: Get first few letters
        first_letters = clues.get('first_letters', '')
        if not first_letters:
            return "What are the first three letters?"
        
        # Step 3: Get last few letters  
        last_letters = clues.get('last_letters', '')
        if not last_letters:
            return "What are the last three letters?"
        
        # Step 4: Get individual letters for middle positions
        # We have first a letters and last b letters, need letters at positions a+1 to n-b-1
        a = len(first_letters)
        b = len(last_letters)
        
        if a + b >= letter_count:
            # We have enough letters, no need to ask for more
            return None
        
        # Find missing positions
        missing_positions = []
        for i in range(a, letter_count - b):
            if f"letter_{i+1}" not in clues:  # 1-indexed
                missing_positions.append(i + 1)
        
        if missing_positions:
            # Ask for the first missing letter
            pos = missing_positions[0]
            return f"What is the {self._ordinal(pos)} letter?"
        
        # If we have all letters, return None to indicate we're done
        return None
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    def has_sufficient_letters(self, clues: Dict[str, Any]) -> bool:
        """Check if we have enough letters to reconstruct the word."""
        letter_count = clues.get('letter_count')
        first_letters = clues.get('first_letters', '')
        last_letters = clues.get('last_letters', '')
        
        if not letter_count:
            return False
        
        a = len(first_letters)
        b = len(last_letters)
        
        # Check if we have all letters
        if a + b >= letter_count:
            return True
        
        # Check if we have individual letters for missing positions
        missing_count = letter_count - a - b
        individual_letters = sum(1 for key in clues.keys() if key.startswith('letter_'))
        
        return individual_letters >= missing_count
    
    def reconstruct_word(self, clues: Dict[str, Any]) -> str:
        """Reconstruct the word from all available clues."""
        letter_count = clues.get('letter_count')
        first_letters = clues.get('first_letters', '')
        last_letters = clues.get('last_letters', '')
        
        if not letter_count:
            return ""
        
        # Start with first letters
        word = list(first_letters)
        
        # Add individual letters for middle positions
        a = len(first_letters)
        for i in range(a, letter_count - len(last_letters)):
            letter_key = f"letter_{i+1}"
            if letter_key in clues:
                word.append(clues[letter_key])
            else:
                word.append('?')  # Missing letter
        
        # Add last letters
        word.extend(list(last_letters))
        
        return ''.join(word)
    
    def reset(self) -> None:
        """Reset the prompt generator for a new level."""
        self.asked_questions.clear()
        self.current_strategy = "initial"
        logger.info("Prompt generator reset")