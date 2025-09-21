"""
Parser to extract clues from Merlin's responses including individual letter positions.
"""
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parses Merlin's responses to extract clues about the secret word."""
    
    def __init__(self):
        pass
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse Merlin's response to extract clues."""
        try:
            clues = {}
            response_lower = response.lower()
            
            # Parse letter count
            letter_count = self._extract_letter_count(response)
            if letter_count:
                clues['letter_count'] = letter_count
            
            # Parse first letters
            first_letters = self._extract_first_letters(response)
            if first_letters:
                clues['first_letters'] = first_letters
            
            # Parse last letters
            last_letters = self._extract_last_letters(response)
            if last_letters:
                clues['last_letters'] = last_letters
            
            # Parse individual letter positions
            individual_letters = self._extract_individual_letters(response)
            clues.update(individual_letters)
            
            # Parse other clues (word type, category, etc.)
            clues.update(self._extract_other_clues(response))
            
            logger.info(f"Parsed clues from response: {clues}")
            return clues
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {}
    
    def _extract_letter_count(self, response: str) -> Optional[int]:
        """Extract letter count from response."""
        try:
            # Look for patterns like "5 letters", "has 5 letters", etc.
            patterns = [
                r'(\d+)\s*letters?',
                r'has\s+(\d+)\s*letters?',
                r'is\s+(\d+)\s*letters?',
                r'word\s+is\s+(\d+)\s*letters?',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.lower())
                if match:
                    return int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting letter count: {e}")
            return None
    
    def _extract_first_letters(self, response: str) -> Optional[str]:
        """Extract first letters from response."""
        try:
            # Look for patterns like "starts with 'ap'", "begins with ap", etc.
            patterns = [
                r'starts?\s+with\s+[\'"]([a-zA-Z]+)[\'"]',
                r'begins?\s+with\s+[\'"]([a-zA-Z]+)[\'"]',
                r'first\s+(\d+)\s+letters?\s+are?\s+[\'"]([a-zA-Z]+)[\'"]',
                r'first\s+letters?\s+are?\s+[\'"]([a-zA-Z]+)[\'"]',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.lower())
                if match:
                    # Return the captured group (letters)
                    return match.group(-1).lower()  # Get the last group (the letters)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting first letters: {e}")
            return None
    
    def _extract_last_letters(self, response: str) -> Optional[str]:
        """Extract last letters from response."""
        try:
            # Look for patterns like "ends with 'le'", "last letters are 'le'", etc.
            patterns = [
                r'ends?\s+with\s+[\'"]([a-zA-Z]+)[\'"]',
                r'last\s+(\d+)\s+letters?\s+are?\s+[\'"]([a-zA-Z]+)[\'"]',
                r'last\s+letters?\s+are?\s+[\'"]([a-zA-Z]+)[\'"]',
                r'finishes?\s+with\s+[\'"]([a-zA-Z]+)[\'"]',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.lower())
                if match:
                    # Return the captured group (letters)
                    return match.group(-1).lower()  # Get the last group (the letters)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting last letters: {e}")
            return None
    
    def _extract_individual_letters(self, response: str) -> Dict[str, str]:
        """Extract individual letter positions from response."""
        clues = {}
        response_lower = response.lower()
        
        # Look for patterns like "4th letter is 'l'", "the 5th letter is 'e'", etc.
        patterns = [
            r'(\d+)(?:st|nd|rd|th)\s+letter\s+is\s+[\'"]([a-zA-Z])[\'"]',
            r'the\s+(\d+)(?:st|nd|rd|th)\s+letter\s+is\s+[\'"]([a-zA-Z])[\'"]',
            r'letter\s+(\d+)\s+is\s+[\'"]([a-zA-Z])[\'"]',
            r'position\s+(\d+)\s+is\s+[\'"]([a-zA-Z])[\'"]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_lower)
            if match:
                position = int(match.group(1))
                letter = match.group(2).lower()
                clues[f'letter_{position}'] = letter
        
        return clues
    
    def _extract_other_clues(self, response: str) -> Dict[str, Any]:
        """Extract other types of clues from response."""
        clues = {}
        response_lower = response.lower()
        
        # Check for word type hints
        if any(word_type in response_lower for word_type in ['noun', 'verb', 'adjective', 'adverb']):
            for word_type in ['noun', 'verb', 'adjective', 'adverb']:
                if word_type in response_lower:
                    clues['word_type'] = word_type
                    break
        
        # Check for category hints
        categories = ['animal', 'food', 'color', 'place', 'object', 'person', 'emotion']
        for category in categories:
            if category in response_lower:
                clues['category'] = category
                break
        
        # Check for definition hints
        if 'definition' in response_lower or 'means' in response_lower:
            clues['has_definition'] = True
        
        # Check for sentence usage
        if 'sentence' in response_lower or 'example' in response_lower:
            clues['has_usage'] = True
        
        return clues
