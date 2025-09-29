"""
Prompt generator for asking Merlin questions to extract individual letters.
"""
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class PromptGenerator:
    def __init__(self):
        self.asked_questions = set()
        self.current_strategy = "initial"
        
    def get_next_prompt(self, clues: Dict[str, Any] = None) -> str:
        """Get the next prompt to ask Merlin."""
        try:
            if not clues:
                return "How many letters?"
            
            return self._get_strategic_prompt(clues)
                
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return "How many letters?"
    
    def _get_strategic_prompt(self, clues: Dict[str, Any]) -> str:
        letter_count = clues.get('letter_count')
        
        # Step 1: Get letter count
        if not letter_count:
            return "How many letters?"
        
        # Step 2: Get first few letters (start with 4, fallback to 3)
        first_letters = clues.get('first_letters', '')
        if not first_letters:
            return  "first four letters?"
        
        # Step 3: Get last few letters  
        last_letters = clues.get('last_letters', '')
        if not last_letters:
            return "last three letters?"
        
        # Step 4: Get individual letters for middle positions
        # We have first a letters and last b letters, need letters at indices a+1 to n-b-1
        a = len(first_letters)
        b = len(last_letters)
        
        if a + b >= letter_count:
            return None
        
        # Find missing indices
        missing_indices = []
        for i in range(a, letter_count - b):
            if f"letter_{i+1}" not in clues:  # 1-indexed
                missing_indices.append(i + 1)
        
        if missing_indices:
            # Ask for the first missing letter
            pos = missing_positions[0]
            return f"the {self._ordinal(pos)} letter?"
        
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
        letter_cnt = clues.get('letter_count')
        first_letters = clues.get('first_letters', '')
        last_letters = clues.get('last_letters', '')
        
        if not letter_cnt:
            return False
        
        a = len(first_letters)
        b = len(last_letters)
        
        # Calculate overlap between first and last letters
        # For a word of length n, if first a letters and last b letters overlap,
        # the overlap is max(0, a + b - n)
        overlap = max(0, a + b - letter_cnt)
        unique_letters = a + b - overlap
        
        if unique_letters >= letter_cnt:
            return True
        
        # Check if we have individual letters for missing indices
        missing_cnt = letter_cnt - unique_letters
        individual_letters = sum(1 for key in clues.keys() if key.startswith('letter_') and key != 'letter_count')
        
        return individual_letters >= missing_cnt
    
    def reconstruct_word(self, clues: Dict[str, Any]) -> str:
        """Reconstruct the word with priority ranking: first four = last letter = first three > rest."""
        letter_count = clues.get('letter_count')
        
        # Use backup clues if available, otherwise use main clues
        first_letters = clues.get('first_letters_backup') or clues.get('first_letters', '')
        last_letters = clues.get('last_letters_backup') or clues.get('last_letters', '')
        
        if not letter_count:
            return ""
        
        # Initialize word array with placeholders
        word = ['?'] * letter_count
        
        # Priority 1: First four letters (highest priority)
        if len(first_letters) == 4:
            for i, letter in enumerate(first_letters):
                if i < letter_count:
                    word[i] = letter
        
        # Priority 2: Last letter (same priority as first four)
        if len(last_letters) == 1:
            word[letter_count - 1] = last_letters[0]
        
        # Priority 3: First three letters (same priority as first four and last letter)
        if len(first_letters) == 3:
            for i, letter in enumerate(first_letters):
                if i < letter_count:
                    # Only fill if position is empty (don't override first four)
                    if word[i] == '?' or len(first_letters) != 4:
                        word[i] = letter
        
        # Priority 4: Fill in remaining last letters (lower priority)
        for i, letter in enumerate(last_letters):
            pos = letter_count - len(last_letters) + i
            if 0 <= pos < letter_count and word[pos] == '?':
                word[pos] = letter
        
        # Priority 5: Individual letters (overrides everything except same priority items)
        for key, letter in clues.items():
            if key.startswith('letter_') and key != 'letter_count':
                try:
                    pos = int(key.split('_')[1]) - 1  # Convert to 0-indexed
                    if 0 <= pos < letter_count:
                        # Check if this conflicts with high priority clues
                        current_letter = word[pos]
                        if current_letter != '?' and current_letter != letter:
                            pass
                        word[pos] = letter
                except (ValueError, IndexError):
                    continue
        
        return ''.join(word)
    
    def reset(self) -> None:
        """Reset for a new level."""
        self.asked_questions.clear()
        self.current_strategy = "initial"
        pass