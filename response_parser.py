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
            
            return clues
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {}
    
    def parse_response_with_expected_count(self, response: str, expected_count: int = None, clue_type: str = None) -> Dict[str, Any]:
        """Parse response with expected count validation for partial matching."""
        try:
            clues = {}
            response_lower = response.lower()
            
            # Parse only the requested clue type if specified
            if clue_type in [None, 'letter_count']:
                letter_count = self._extract_letter_count(response)
                if letter_count:
                    clues['letter_count'] = letter_count
            
            # Parse first letters with expected count
            if clue_type in ['first_letters', None]:
                first_letters = self._extract_first_letters(response)
                # Fallback: accept only if response is bare letters token (e.g., "TROP")
                if not first_letters:
                    cleaned = re.sub(r'[^a-zA-Z]', '', response)
                    if re.fullmatch(r'\s*[A-Za-z]+\s*', response) and cleaned:
                        if not expected_count or len(cleaned) <= expected_count:
                            first_letters = cleaned.lower()
                if first_letters:
                    clues['first_letters'] = first_letters
            
            # Parse last letters with expected count
            if clue_type in ['last_letters', None]:
                last_letters = self._extract_last_letters(response)
                # Fallback: accept only if response is bare letters token
                if not last_letters:
                    cleaned = re.sub(r'[^a-zA-Z]', '', response)
                    if re.fullmatch(r'\s*[A-Za-z]+\s*', response) and cleaned:
                        if not expected_count or len(cleaned) <= expected_count:
                            last_letters = cleaned.lower()
                if last_letters:
                    clues['last_letters'] = last_letters
            
            # Parse individual letter positions only if not constrained to other types
            if clue_type in [None, 'individual']:
                individual_letters = self._extract_individual_letters(response)
                clues.update(individual_letters)
            
            return clues
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {}
    
    def _extract_letter_count(self, response: str) -> Optional[int]:
        """Extract letter count from response."""
        try:
            # First try to extract digit patterns (avoid matching "first X letters" or "last X letters")
            patterns = [
                r'(\d+)\s*letters?[,\s]',  # "5 letters," or "5 letters "
                r'has\s+(\d+)\s*letters?',
                r'is\s+(\d+)\s*letters?',
                r'word\s+is\s+(\d+)\s*letters?',
                r'(\d+)\s*letters?$',  # "5 letters" at end of sentence
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.lower())
                if match:
                    return int(match.group(1))
            
            # Then try word-to-number conversion for patterns like "seven letters"
            word_to_number = {
                'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
                'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
                'ten': 10, 'eleven': 11, 'twelve': 12
            }
            
            response_lower = response.lower()
            for word, number in word_to_number.items():
                # Only match if it's not part of "first X letters" or "last X letters"
                if (f'{word} letters' in response_lower and 
                    f'first {word} letters' not in response_lower and
                    f'last {word} letters' not in response_lower):
                    return number
            
            # Finally, accept bare number words or digits as the entire response
            # e.g., "Six" or "6"
            bare_digit = re.fullmatch(r'\s*(\d+)\s*', response_lower)
            if bare_digit:
                try:
                    return int(bare_digit.group(1))
                except ValueError:
                    pass
            if response_lower.strip() in word_to_number:
                return word_to_number[response_lower.strip()]
            
            return None
            
        except Exception as e:
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
                r'first\s+(?:\d+|\w+)\s+letters?\s+are\s+(.+)',
                r'first\s+letters?\s+are\s+(.+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    # Get the letters group (last group with actual letters)
                    groups = match.groups()
                    letters_group = groups[-1]  # Get the last group (the letters)
                    
                    # Clean up the letters (remove ", and" pattern and all non-letter characters)
                    letters = letters_group.replace(', and', '').replace(' and ', '')
                    letters = re.sub(r'[^a-zA-Z]', '', letters)
                    return letters.lower()
            
            return None
            
        except Exception as e:
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
                # Handle "The last three letters of the password are RON."
                r'last\s+(?:\d+|\w+)\s+letters?\s+(?:of\s+the\s+password\s+)?are\s+(.+)',
                r'last\s+letters?\s+(?:of\s+the\s+password\s+)?are\s+(.+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    # Get the letters group (last group with actual letters)
                    groups = match.groups()
                    letters_group = groups[-1]  # Get the last group (the letters)
                    
                    # Clean up the letters (remove ", and" pattern and all non-letter characters)
                    letters = letters_group.replace(', and', '').replace(' and ', '')
                    letters = re.sub(r'[^a-zA-Z]', '', letters)
                    return letters.lower()
            
            return None
            
        except Exception as e:
            return None
    
    def _extract_individual_letters(self, response: str) -> Dict[str, str]:
        """Extract individual letter positions from response."""
        clues = {}
        response_lower = response.lower()
        
        # Look for patterns like "4th letter is 'l'", "the 5th letter is 'e'", etc.
        patterns = [
            # Patterns with quotes
            r'(\d+)(?:st|nd|rd|th)\s+letter\s+is\s+[\'"]([a-zA-Z])[\'"]',
            r'the\s+(\d+)(?:st|nd|rd|th)\s+letter\s+is\s+[\'"]([a-zA-Z])[\'"]',
            r'letter\s+(\d+)\s+is\s+[\'"]([a-zA-Z])[\'"]',
            r'position\s+(\d+)\s+is\s+[\'"]([a-zA-Z])[\'"]',
            # Handle word ordinals like "fourth letter is 'F'" (with quotes)
            r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+letter\s+(?:of\s+the\s+password\s+)?is\s+[\'"]([a-zA-Z])[\'"]',
            r'the\s+(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+letter\s+(?:of\s+the\s+password\s+)?is\s+[\'"]([a-zA-Z])[\'"]',
            # Patterns without quotes - numeric ordinals
            r'(\d+)(?:st|nd|rd|th)\s+letter\s+is\s+([a-zA-Z])\.?',
            r'the\s+(\d+)(?:st|nd|rd|th)\s+letter\s+is\s+([a-zA-Z])\.?',
            # Patterns without quotes - word ordinals
            r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+letter\s+(?:of\s+the\s+password\s+)?is\s+([a-zA-Z])\.?',
            r'the\s+(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+letter\s+(?:of\s+the\s+password\s+)?is\s+([a-zA-Z])\.?',
        ]
        
        word_to_number = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
            'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10
        }
        
        for pattern in patterns:
            match = re.search(pattern, response_lower)
            if match:
                position_str = match.group(1)
                letter = match.group(2).lower()
                
                # Convert position to number
                if position_str.isdigit():
                    position = int(position_str)
                else:
                    position = word_to_number.get(position_str.lower())
                
                if position:
                    clues[f'letter_{position}'] = letter
        
        return clues