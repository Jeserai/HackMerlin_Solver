"""
HackMerlin Solver - AI Prompt Engineering Challenge with improved strategy.
"""
import logging
import time
from typing import Dict, Any, List
from game_automation import GameAutomation
from resource_manager import ResourceManager
from prompt_generator import PromptGenerator
from response_parser import ResponseParser
from config import MAX_QUESTIONS_PER_LEVEL, MAX_RETRIES_PER_LEVEL, RESOURCE_LEVELS

# Minimal logging for manual mode
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class HackMerlinSolver:
    """HackMerlin solver with improved letter extraction strategy."""
    
    def __init__(self, resource_level: str = 'low'):
        self.game_automation = GameAutomation()
        self.resource_manager = ResourceManager(resource_level)
        self.prompt_generator = PromptGenerator()
        self.response_parser = ResponseParser()
        self.max_questions_per_level = MAX_QUESTIONS_PER_LEVEL
        self.max_retries_per_level = MAX_RETRIES_PER_LEVEL
        
    
    def run(self) -> None:
        """Run the main game loop."""
        try:
            # Setup game automation
            self.game_automation.setup_driver()
            self.game_automation.navigate_to_game()
            
            # Solve a single level in manual mode
            success = self._solve_level()
            self.prompt_generator.reset()
            
        except Exception as e:
            logger.error(f"Error in main game loop: {e}")
            raise
        finally:
            self.game_automation.close()
    
    def _solve_level(self) -> bool:
        """Solve the current level using the improved strategy."""
        try:
            clues = {}
            original_clues = {}  # Store original clues before any modifications
            questions_asked = 0
            
            # Ask Merlin questions to gather clues systematically
            while questions_asked < self.max_questions_per_level:
                # Generate next prompt based on current clues
                prompt = self.prompt_generator.get_next_prompt(clues)
                
                if prompt is None:
                    # No more prompts needed, we have sufficient information
                    pass
                    break
                
                # Ask Merlin and get response
                response = self.game_automation.ask_merlin(prompt)
                if not response:
                    logger.error("No response from Merlin")
                    break
                
                # Parse response - use LLM if configured, otherwise use regex parser
                if self.resource_manager.word_matcher.config['use_llm']:
                    new_clues = self.resource_manager.word_matcher.parse_response_with_llm(response, prompt)
                else:
                    # Parse response with context to extract clues
                    expected_count = None
                    clue_type = None
                    pl = prompt.lower()
                    if 'how many letters' in pl:
                        clue_type = 'letter_count'
                    elif 'first' in pl:
                        clue_type = 'first_letters'
                        if 'four' in pl:
                            expected_count = 4
                        elif 'three' in pl:
                            expected_count = 3
                    elif 'last' in pl:
                        clue_type = 'last_letters'
                        if 'two' in pl:
                            expected_count = 2
                        elif 'three' in pl:
                            expected_count = 3
                        elif 'four' in pl:
                            expected_count = 4
                    else:
                        # Might be individual letters
                        clue_type = None
                    new_clues = self.response_parser.parse_response_with_expected_count(response, expected_count, clue_type)
                clues.update(new_clues)
                
                questions_asked += 1
                
                # Check if we have enough letters to reconstruct the word
                if self.prompt_generator.has_sufficient_letters(clues):
                    break
                
                time.sleep(1)  # Brief pause between questions
            
            # Try to reconstruct the word
            reconstructed_word = self.prompt_generator.reconstruct_word(clues)
            if reconstructed_word:
                pass
            
            # Try to find the best word based on clues
            if self.resource_manager.word_matcher.config['use_llm']:
                # Use LLM for word generation
                best_word = self.resource_manager.word_matcher.generate_word_with_llm(clues)
            else:
                # Use configured strategy (concatenation/embeddings)
                best_word = self.resource_manager.find_best_word(clues)
            
            if not best_word:
                return False
            
            # Store original clues before submitting (in case we need to retry)
            original_clues = clues.copy()
            
            # Submit the word guess with retry logic
            success = self._submit_with_retry(best_word, original_clues)
            
            return success
            
        except Exception as e:
            logger.error(f"Error solving level: {e}")
            return False
    
    def _submit_with_retry(self, word: str, clues: Dict[str, Any]) -> bool:
        """Submit word guess with expanded retry strategy."""
        # In manual mode, implement expanded retry strategy
        if self.game_automation.manual_mode:
            success = self.game_automation.submit_word_guess(word)
            if success:
                return True
            else:
                return self._backup_prompt_strategy(clues)
        
        # Automated retry logic for Selenium mode
        for attempt in range(self.max_retries_per_level):
            
            # Submit the word guess
            success = self.game_automation.submit_word_guess(word)
            
            if success:
                logger.info(f"Successfully guessed word: {word}")
                return True
            
            
            # Try candidate-based retry strategy
            if attempt < self.max_retries_per_level - 1:
                success = self._backup_prompt_strategy(clues)
                if success:
                    return True
        
        return False
    
    def _backup_prompt_strategy(self, clues: Dict[str, Any]) -> bool:
        """Implement candidate-based retry strategy with length variations."""
        try:
            original_letter_count = clues.get('letter_count', 0)
            first_letters = clues.get('first_letters', '')
            last_letters = clues.get('last_letters', '')
            
            if not original_letter_count:
                return False
            
            # Systematic backup prompt strategy
            
            # Generate systematic backup prompts: first 3 → 4th → 5th → ... → nth → last letter
            backup_prompts = self._generate_systematic_backup_prompts(original_letter_count, first_letters, last_letters)
            
            # Try each backup prompt and update original clues
            for prompt_info in backup_prompts:
                prompt = prompt_info['prompt']
                strategy_name = prompt_info['strategy']
                
                print(f"\n📝 BACKUP PROMPT:")
                print(f"   {prompt}")
                print("\n⏳ Please copy this prompt, paste it to Merlin, and wait for response...")
                response = input("📥 MERLIN'S RESPONSE: ").strip()
                
                if response:
                    # Parse response - use LLM if configured, otherwise use regex parser
                    if self.resource_manager.word_matcher.config['use_llm']:
                        new_clues = self.resource_manager.word_matcher.parse_response_with_llm(response, prompt)
                    else:
                        # Parse response with expected count validation
                        expected_count = None
                        clue_type = None
                        
                        if "first" in prompt.lower():
                            if "three" in prompt.lower():
                                expected_count = 3
                            clue_type = "first_letters"
                        elif "last" in prompt.lower():
                            clue_type = "last_letters"
                            if "last two" in prompt.lower():
                                expected_count = 2
                            elif "last three" in prompt.lower():
                                expected_count = 3
                            elif "last four" in prompt.lower():
                                expected_count = 4
                            elif "last letter" in prompt.lower():
                                expected_count = 1
                        elif "letter" in prompt.lower() and any(ordinal in prompt.lower() for ordinal in ["4th", "5th", "6th", "7th", "8th"]):
                            clue_type = "individual"
                        
                        new_clues = self.response_parser.parse_response_with_expected_count(response, expected_count, clue_type)
                    
                    # Update original clues with new information (primary approach)
                    # Special merge behavior: if we asked for the last letter, update only the last character of last_letters
                    if "last_letters" in new_clues and clue_type == "last_letters" and expected_count == 1:
                        new_last_char = new_clues["last_letters"][-1]
                        existing_last = clues.get("last_letters", "")
                        if existing_last:
                            clues["last_letters"] = existing_last[:-1] + new_last_char
                        else:
                            clues["last_letters"] = new_last_char
                    else:
                        clues.update(new_clues)
                    
                    # Try to generate word with updated clues
                    if self.resource_manager.word_matcher.config['use_llm']:
                        reconstructed_word = self.resource_manager.word_matcher.generate_word_with_llm(clues)
                    else:
                        reconstructed_word = self.prompt_generator.reconstruct_word(clues)
                    
                    if reconstructed_word and '?' not in reconstructed_word:
                        print(f"\n🎯 UPDATED WORD GUESS:")
                        print(f"   {reconstructed_word}")
                        print("\n⏳ Please submit this word to the game...")
                        correct = input("✅ Was the guess correct? (y/n): ").strip().lower()
                        
                        if correct == 'y':
                            return True
                        else:
                            # Continue with next backup prompt
                            continue
                    else:
                        pass
            
            # If original length is 7, try length variations as candidates
            if original_letter_count == 7:
                candidate_lengths = [6, 8]  # Try 6 and 8 for length 7
                
                for candidate_length in candidate_lengths:
                    # Create candidate clues with new length
                    candidate_clues = clues.copy()
                    candidate_clues['letter_count'] = candidate_length
                    
                    # Try to reconstruct word with candidate length
                    reconstructed_word = self.prompt_generator.reconstruct_word(candidate_clues)
                    if reconstructed_word and '?' not in reconstructed_word:
                        best_word = self.resource_manager.find_best_word(candidate_clues)
                        
                        print(f"\n🎯 CANDIDATE LENGTH {candidate_length} WORD:")
                        print(f"   {best_word}")
                        print("\n⏳ Please submit this candidate word to the game...")
                        correct = input("✅ Was the candidate correct? (y/n): ").strip().lower()
                        
                        if correct == 'y':
                            return True
                        else:
                            # Continue with next candidate length
                            continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error in candidate strategy: {e}")
            return False
    
    def _generate_systematic_backup_prompts(self, letter_count: int, first_letters: str, last_letters: str) -> List[Dict[str, str]]:
        """Generate systematic backup prompts: [first 3 letters, 4th letter, 5th letter, ..., nth letter, last letter]."""
        prompts = []
        
        # 1. Last letter first (highest value clarification)
        if len(last_letters) != 1:
            prompts.append({
                'prompt': "What is the last letter?",
                'strategy': 'last_letter'
            })

        # 2. First three letters (if we don't have them or have more)
        if len(first_letters) != 3:
            prompts.append({
                'prompt': "What are the first three letters?",
                'strategy': 'first_3_letters'
            })
        
        # 3. Individual letters from 4th to nth
        for pos in range(4, letter_count + 1):
            ordinal = self._ordinal(pos)
            prompts.append({
                'prompt': f"What is the {ordinal} letter?",
                'strategy': f'letter_{pos}'
            })
        
        # 4. Last two letters (if we don't have them or have more)
        if len(last_letters) != 2:
            prompts.append({
                'prompt': "What are the last two letters?",
                'strategy': 'last_two_letters'
            })
        
        # 5. (No-op) last letter already first
        
        return prompts
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    def _try_candidate_strategy(self, clues: Dict[str, Any], candidate_length: int, strategy_name: str, prompt: str) -> bool:
        """Try a specific candidate strategy with given length."""
        try:
            if self.game_automation.manual_mode:
                print(f"\n📝 CANDIDATE PROMPT:")
                print(f"   {prompt}")
                print("\n⏳ Please copy this prompt, paste it to Merlin, and wait for response...")
                response = input("📥 MERLIN'S RESPONSE: ").strip()
                
                if response:
                    # Parse with expected count validation
                    expected_count = None
                    clue_type = None
                    
                    if "first" in prompt.lower():
                        if "four" in prompt.lower():
                            expected_count = 4
                        elif "three" in prompt.lower():
                            expected_count = 3
                        clue_type = "first_letters"
                    elif "last" in prompt.lower():
                        if "four" in prompt.lower():
                            expected_count = 4
                        elif "three" in prompt.lower():
                            expected_count = 3
                        clue_type = "last_letters"
                    
                    new_clues = self.response_parser.parse_response_with_expected_count(response, expected_count, clue_type)
                    
                    # Create candidate clues with the new length
                    candidate_clues = clues.copy()
                    candidate_clues['letter_count'] = candidate_length
                    
                    # Handle backup clues intelligently - don't overwrite main clues
                    for key, value in new_clues.items():
                        if key == 'first_letters' and 'first' in strategy_name and 'backup' in strategy_name:
                            # This is a backup first letters request - store as backup
                            candidate_clues['first_letters_backup'] = value
                        elif key == 'last_letters' and 'last' in strategy_name and 'backup' in strategy_name:
                            # This is a backup last letters request - store as backup
                            candidate_clues['last_letters_backup'] = value
                        else:
                            # Regular update
                            candidate_clues[key] = value
                    
                    # Try to reconstruct word with candidate clues
                    reconstructed_word = self.prompt_generator.reconstruct_word(candidate_clues)
                    if reconstructed_word and '?' not in reconstructed_word:
                        print(f"\n🎯 CANDIDATE WORD GUESS:")
                        print(f"   {reconstructed_word}")
                        print("\n⏳ Please submit this word to the game...")
                        correct = input("✅ Was the guess correct? (y/n): ").strip().lower()
                        
                        if correct == 'y':
                            # Update original clues with the successful candidate
                            clues.update(candidate_clues)
                            return True
                        else:
                            pass
            
            return False
            
        except Exception as e:
            logger.error(f"Error in candidate strategy {strategy_name}: {e}")
            return False


def main():
    """Main entry point (manual mode, concise)."""
    solver = HackMerlinSolver(resource_level='low')
    try:
        solver.run()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == "__main__":
    main()