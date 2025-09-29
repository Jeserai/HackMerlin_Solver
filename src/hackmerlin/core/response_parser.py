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
            letter_cnt = self._extract_letter_count(response)
            if letter_cnt:
                clues['letter_count'] = letter_cnt
            
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
    
    def parse_response_with_context(self, response: str, prompt: str) -> Dict[str, Any]:
        """Parse response with context from the prompt to avoid wrong extractions."""
        try:
            clues = {}
            prompt_lower = prompt.lower()
            
            # Parse letter count if asked
            if 'how many letters' in prompt_lower:
                letter_count = self._extract_letter_count(response)
                if letter_count:
                    clues['letter_count'] = letter_count
            
            # Parse first letters if asked
            elif 'first' in prompt_lower:
                first_letters = self._extract_first_letters(response)
                if first_letters:
                    clues['first_letters'] = first_letters
            
            # Parse last letters if asked
            elif 'last' in prompt_lower:
                last_letters = self._extract_last_letters(response)
                if last_letters:
                    clues['last_letters'] = last_letters
            
            # Parse individual letters if asked
            elif any(ordinal in prompt_lower for ordinal in ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th']):
                individual_letters = self._extract_individual_letters(response)
                clues.update(individual_letters)
            
            # Fallback: parse all if context is unclear
            else:
                clues = self.parse_response(response)
            
            return clues
            
        except Exception as e:
            logger.error(f"Error parsing response with context: {e}")
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
        """Extract letter count from response by searching for numbers 1-10 or words one-ten."""
        try:
            response_lower = response.lower()
            
            # Word to number mapping
            word_to_number = {
                'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
            }
            
            # Prioritize word numbers over digits to avoid false matches
            # Check for word numbers one-ten first, but only if they appear with "letter" or at start
            for word, number in word_to_number.items():
                if word in response_lower:
                    # Check if this word appears near "letter" or at the start of response
                    words = response_lower.split()
                    try:
                        word_index = words.index(word)
                        nearby_words = words[max(0, word_index-2):word_index+3]
                        if (response_lower.startswith(word) or 
                            any('letter' in w for w in nearby_words)):
                            return number
                    except ValueError:
                        # Word not found in split words (might be part of another word)
                        continue
            
            # Then check for digit numbers 1-10, but only if they appear with "letter" or are standalone
            # This avoids matching random digits in the response
            for i in range(1, 11):
                if str(i) in response_lower:
                    # Check if this digit appears near "letter" to confirm it's about letter count
                    words = response_lower.split()
                    for j, word in enumerate(words):
                        if str(i) in word:
                            # Check if "letter" appears nearby (within 3 words) OR if it's a standalone digit
                            nearby_words = words[max(0, j-3):j+4]
                            if (any('letter' in w for w in nearby_words) or 
                                word.strip() == str(i)):  # Standalone digit
                                return i
            
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
                # Handle "The first four letters of the password are C-I-R-C."
                r'first\s+(?:\d+|\w+)\s+letters?\s+(?:of\s+the\s+password\s+)?are\s+(.+)',
                r'first\s+letters?\s+(?:of\s+the\s+password\s+)?are\s+(.+)',
                r'first\s+(?:\d+|\w+)\s+letters?\s+are\s+(.+)',
                r'first\s+letters?\s+are\s+(.+)',
                # Handle quoted words at start of response
                r'^["\']([A-Za-z]+)["\']',
                # Handle direct letter sequences like "JAGU" or "C-I-R-C"
                r'^([A-Z]+(?:-[A-Z]+)*\.?)$',
                r'^([A-Z]+)$',
                # Handle dots between letters like "Z... E... P... H..."
                r'^([A-Z](?:\.\.\.\s*[A-Z])*\.*)$',
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
                    
                    if letters:
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
                # Handle "The password ends with T." or "The password ends with LEE."
                r'(?:password\s+)?ends?\s+with\s+[\\"\']?([A-Z]+)[\\"\']?\.?',
                r'(?:password\s+)?ends?\s+with\s+([A-Z]+)\.?',
                r'last\s+(?:\d+|\w+)\s+letters?\s+(?:of\s+the\s+password\s+)?are\s+(.+)',
                r'last\s+letters?\s+(?:of\s+the\s+password\s+)?are\s+(.+)',
                # Handle direct letter lists like "A, R, and R." or "JAGU"
                r'^([A-Z]+(?:,\s*[A-Z]+)*\.?)$',
                r'^([A-Z]+(?:,\s*[A-Z]+)*)$',
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
                    
                    if letters:
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