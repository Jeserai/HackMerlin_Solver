"""
Word matcher for HackMerlin game - direct concatenation or LLM-based.
"""
import logging
from typing import Optional, Dict, Any
from config import RESOURCE_LEVELS, OPENAI_API_KEY, HUGGINGFACE_API_KEY, OPENAI_MODEL, HUGGINGFACE_MODEL

logger = logging.getLogger(__name__)


class WordMatcher:
    """Word matcher that reconstructs words from individual letters or uses LLM."""
    
    def __init__(self, resource_level: str = 'low'):
        self.resource_level = resource_level
        self.config = RESOURCE_LEVELS.get(resource_level, RESOURCE_LEVELS['low'])
        self.llm_client = None
        self.embeddings_model = None
        
        # Initialize LLM if configured
        if self.config['use_llm']:
            self._setup_llm()
        
        # Initialize embeddings if configured
        if self.config['use_embeddings']:
            self._setup_embeddings()
    
    def _setup_llm(self) -> None:
        """Setup LLM client."""
        try:
            if OPENAI_API_KEY:
                import openai
                openai.api_key = OPENAI_API_KEY
                self.llm_client = openai
                logger.info("OpenAI LLM client initialized")
            else:
                # Try HuggingFace local models
                try:
                    from transformers import pipeline
                    self.llm_client = pipeline("text-generation", model=HUGGINGFACE_MODEL)
                    logger.info("HuggingFace LLM client initialized (local model)")
                except Exception as hf_error:
                    logger.warning(f"HuggingFace model setup failed: {hf_error}")
                    logger.warning("LLM disabled - no OpenAI API key and HuggingFace model unavailable")
                    self.config['use_llm'] = False
        except Exception as e:
            logger.warning(f"Failed to setup LLM: {e}")
            self.config['use_llm'] = False
    
    def _setup_embeddings(self) -> None:
        """Setup embeddings model."""
        try:
            import gensim.downloader as api
            self.embeddings_model = api.load("word2vec-google-news-300")
            logger.info("Word2Vec embeddings model loaded")
        except Exception as e:
            logger.warning(f"Failed to load embeddings model: {e}")
            self.config['use_embeddings'] = False
    
    def find_best_match(self, clues: Dict[str, Any]) -> Optional[str]:
        """Find the best word based on strategy and available clues."""
        try:
            strategy = self.config['strategy']
            
            if strategy == 'concatenation':
                return self._direct_concatenation(clues)
            elif strategy == 'llm':
                return self._llm_prediction(clues)
            elif strategy == 'embeddings':
                return self._embedding_search(clues)
            else:
                return self._direct_concatenation(clues)
                
        except Exception as e:
            logger.error(f"Error finding word: {e}")
            return self._direct_concatenation(clues)
    
    def _direct_concatenation(self, clues: Dict[str, Any]) -> Optional[str]:
        """Direct concatenation of letters - most efficient approach."""
        try:
            letter_count = clues.get('letter_count')
            first_letters = clues.get('first_letters', '')
            last_letters = clues.get('last_letters', '')
            
            if not letter_count:
                return None
            
            # Build word from available letters
            word = ['?'] * letter_count
            
            # Fill in first letters
            for i, letter in enumerate(first_letters):
                if i < letter_count:
                    word[i] = letter
            
            # Fill in last letters
            for i, letter in enumerate(last_letters):
                pos = letter_count - len(last_letters) + i
                if pos >= 0 and pos < letter_count:
                    word[pos] = letter
            
            # Fill in individual letters
            for key, letter in clues.items():
                if key.startswith('letter_'):
                    try:
                        pos = int(key.split('_')[1]) - 1  # Convert to 0-indexed
                        if 0 <= pos < letter_count:
                            word[pos] = letter
                    except (ValueError, IndexError):
                        continue
            
            # Check if we have all letters
            if '?' not in word:
                return ''.join(word)
            
            # If missing letters, fill with common letters
            vowels = ['a', 'e', 'i', 'o', 'u']
            consonants = ['r', 's', 't', 'n', 'l']
            common_letters = vowels + consonants
            
            for i, letter in enumerate(word):
                if letter == '?':
                    word[i] = common_letters[i % len(common_letters)]
            
            return ''.join(word)
            
        except Exception as e:
            logger.error(f"Error in direct concatenation: {e}")
            return None
    
    def _llm_prediction(self, clues: Dict[str, Any]) -> Optional[str]:
        """Use LLM to predict the word from clues."""
        try:
            if not self.llm_client:
                return self._direct_concatenation(clues)
            
            # Build prompt for LLM
            prompt = self._build_llm_prompt(clues)
            
            if OPENAI_API_KEY and hasattr(self.llm_client, 'chat'):
                # OpenAI API
                response = self.llm_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a word puzzle solver. Given clues about a word, predict the most likely word."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                word = response.choices[0].message.content.strip().lower()
            else:
                # HuggingFace pipeline
                response = self.llm_client(prompt, max_length=50, num_return_sequences=1)
                word = response[0]['generated_text'].split()[-1].lower()
            
            # Validate word matches clues
            if self._validate_word(word, clues):
                return word
            
            # Fallback to direct concatenation if LLM result is invalid
            return self._direct_concatenation(clues)
            
        except Exception as e:
            logger.error(f"LLM prediction failed: {e}")
            return self._direct_concatenation(clues)
    
    def _embedding_search(self, clues: Dict[str, Any]) -> Optional[str]:
        """Use embeddings to find similar words."""
        try:
            if not self.embeddings_model:
                return self._direct_concatenation(clues)
            
            # First try direct concatenation
            direct_word = self._direct_concatenation(clues)
            if direct_word and direct_word in self.embeddings_model:
                return direct_word
            
            # If direct word not in embeddings, try to find similar words
            letter_count = clues.get('letter_count')
            if not letter_count:
                return direct_word
            
            # Get words of correct length from embeddings
            candidate_words = [
                word for word in self.embeddings_model.index_to_key 
                if len(word) == letter_count
            ]
            
            if not candidate_words:
                return direct_word
            
            # Score words based on how well they match our clues
            best_word = None
            best_score = 0
            
            for word in candidate_words:
                score = self._score_word_match(word, clues)
                if score > best_score:
                    best_score = score
                    best_word = word
            
            return best_word if best_word else direct_word
            
        except Exception as e:
            logger.error(f"Embedding search failed: {e}")
            return self._direct_concatenation(clues)
    
    def _build_llm_prompt(self, clues: Dict[str, Any]) -> str:
        """Build prompt for LLM based on clues."""
        letter_count = clues.get('letter_count', 'unknown')
        first_letters = clues.get('first_letters', '')
        last_letters = clues.get('last_letters', '')
        
        prompt = f"Find a {letter_count}-letter English word"
        
        if first_letters:
            prompt += f" that starts with '{first_letters}'"
        
        if last_letters:
            prompt += f" and ends with '{last_letters}'"
        
        # Add individual letter clues
        individual_letters = []
        for key, letter in clues.items():
            if key.startswith('letter_'):
                try:
                    pos = int(key.split('_')[1])
                    individual_letters.append(f"position {pos}: '{letter}'")
                except (ValueError, IndexError):
                    continue
        
        if individual_letters:
            prompt += f". Individual letters: {', '.join(individual_letters)}"
        
        prompt += ". Return only the word, nothing else."
        
        return prompt
    
    def _validate_word(self, word: str, clues: Dict[str, Any]) -> bool:
        """Validate that word matches the clues."""
        try:
            letter_count = clues.get('letter_count')
            first_letters = clues.get('first_letters', '')
            last_letters = clues.get('last_letters', '')
            
            # Check length
            if len(word) != letter_count:
                return False
            
            # Check first letters
            if first_letters and not word.startswith(first_letters):
                return False
            
            # Check last letters
            if last_letters and not word.endswith(last_letters):
                return False
            
            # Check individual letters
            for key, expected_letter in clues.items():
                if key.startswith('letter_'):
                    try:
                        pos = int(key.split('_')[1]) - 1  # Convert to 0-indexed
                        if pos >= len(word) or word[pos] != expected_letter:
                            return False
                    except (ValueError, IndexError):
                        continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating word: {e}")
            return False
    
    def _score_word_match(self, word: str, clues: Dict[str, Any]) -> float:
        """Score how well a word matches the clues."""
        score = 0.0
        
        # Score first letters match
        first_letters = clues.get('first_letters', '')
        if first_letters:
            if word.startswith(first_letters):
                score += len(first_letters) * 2.0
            else:
                # Partial match
                for i, letter in enumerate(first_letters):
                    if i < len(word) and word[i] == letter:
                        score += 1.0
        
        # Score last letters match
        last_letters = clues.get('last_letters', '')
        if last_letters:
            if word.endswith(last_letters):
                score += len(last_letters) * 2.0
            else:
                # Partial match
                for i, letter in enumerate(reversed(last_letters)):
                    if i < len(word) and word[-(i+1)] == letter:
                        score += 1.0
        
        # Score individual letters match
        for key, expected_letter in clues.items():
            if key.startswith('letter_'):
                try:
                    pos = int(key.split('_')[1]) - 1
                    if pos < len(word) and word[pos] == expected_letter:
                        score += 3.0  # Individual letter matches are highly weighted
                except (ValueError, IndexError):
                    continue
        
        return score