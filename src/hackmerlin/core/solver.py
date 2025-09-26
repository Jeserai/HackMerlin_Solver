"""
HackMerlin Solver - AI Prompt Engineering Challenge with improved strategy.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from .game_automation import GameAutomation
from ..ai.resource_manager import ResourceManager
from .prompt_generator import PromptGenerator
from .response_parser import ResponseParser
from ..utils.config import MAX_QUESTIONS_PER_LEVEL, MAX_RETRIES_PER_LEVEL, RESOURCE_LEVELS, LOG_LEVEL

# Configure logging to show all messages
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class HackMerlinSolver:
    """HackMerlin solver with improved letter extraction strategy."""
    
    def __init__(self, resource_level: str = 'low', use_playwright: bool = False):
        self.game_automation = GameAutomation(use_playwright=use_playwright)
        self.resource_manager = ResourceManager(resource_level)
        self.prompt_generator = PromptGenerator()
        self.response_parser = ResponseParser()
        self.max_questions_per_level = MAX_QUESTIONS_PER_LEVEL
        self.max_retries_per_level = MAX_RETRIES_PER_LEVEL
    
    def _filter_word(self, word: str) -> str:
        """Filter out non-Latin characters from word."""
        if not word:
            return word
        # Keep only ASCII alphabetic characters
        filtered = ''.join(c for c in word if c.isascii() and c.isalpha())
        if filtered != word:
            logger.info(f"🔧 Filtered word: '{word}' → '{filtered}'")
        return filtered
    
    def _is_denial_response(self, response: str) -> bool:
        """Check if Merlin's response indicates a denial/refusal to answer."""
        if not response:
            return False
        
        response_lower = response.lower()
        denial_phrases = [
            "cannot", "can't", "sorry", "i am sorry", "i cannot", "i can't",
            "cannot tell", "cannot reveal", "cannot say", "cannot provide",
            "refuse", "unable", "not allowed", "forbidden", "restricted",
            "i'm sorry", "apologize", "regret", "unfortunately"
        ]
        
        return any(phrase in response_lower for phrase in denial_phrases)
    
        
    
    def run(self) -> None:
        """Run the main game loop."""
        try:
            # Setup game automation
            self.game_automation.setup_driver()
            self.game_automation.navigate_to_game()
            
            level_count = 0
            
            while True:
                level_count += 1
                print(f"\n🎮 Starting Level {level_count}")
                logger.info(f"🎮 Starting Level {level_count}")
                
                # Solve the current level
                success = self._solve_level()
                self.prompt_generator.reset()
                
                if success:
                    print("🎉 Level completed successfully!")
                    logger.info("🎉 Level completed successfully!")
                    
                    # Check if we can continue to next level
                    if self.game_automation.use_playwright:
                        # In Playwright mode, check if browser is still alive
                        if self.game_automation.page:
                            print("🔄 Browser still alive - automatically continuing to next level!")
                            logger.info("🔄 Browser still alive - automatically continuing to next level!")
                            continue
                        else:
                            print("💡 Browser closed - cannot continue to next level")
                            logger.info("💡 Browser closed - cannot continue")
                            break
                    else:
                        # In manual mode, we can continue to next level
                        print("🔄 Manual mode - continuing to next level!")
                        logger.info("🔄 Manual mode - continuing to next level!")
                        continue
                else:
                    print("❌ Level failed - automatically retrying...")
                    logger.info("❌ Level failed - automatically retrying...")
                    level_count -= 1  # Don't increment level count for retry
                    continue
            
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
            
            # For the first level, try the simple "what is the password" approach first
            # (only for Level 1, not for higher levels)
            current_level = self.game_automation.get_current_level()
            if current_level == 0:  # Level 0 is the first level only
                logger.info("🎯 First level: Trying simple 'what is the password' approach")
                response = self.game_automation.ask_merlin("What is the password?")
                if response and response.lower() not in ['i cannot tell you', 'cannot say', 'i cannot provide that information']:
                    logger.info(f"🔑 Direct password response: {response}")
                    # Try to extract the password from the response
                    import re
                    
                    # Pattern 1: "the password is X" or "password is none other than X"
                    password_match = re.search(r'the password is (?:none other than )?["\']?([A-Z]+)["\']?', response, re.IGNORECASE)
                    if not password_match:
                        # Pattern 2: "password you seek is X" or "password is X"
                        password_match = re.search(r'password (?:you )?seek is ["\']?([A-Z]+)["\']?', response, re.IGNORECASE)
                    if not password_match:
                        # Pattern 3: "password is X" (more specific)
                        password_match = re.search(r'password is ["\']?([A-Z]+)["\']?', response, re.IGNORECASE)
                    if not password_match:
                        # Pattern 4: Words in quotes (prioritize uppercase words)
                        password_match = re.search(r'"([A-Z]+)"', response)
                    if not password_match:
                        # Pattern 5: Single standalone uppercase word (4+ letters)
                        words = response.split()
                        for word in words:
                            if len(word) >= 4 and word.isalpha() and word.isupper():
                                password_match = re.search(r'\b' + re.escape(word) + r'\b', response)
                                if password_match:
                                    break
                    
                    if password_match:
                        # Extract the password based on which pattern matched
                        if password_match.groups():  # Pattern with groups (Pattern 1 & 2)
                            password = password_match.group(1)
                        else:  # Pattern without groups (Pattern 3 & 4)
                            password = password_match.group(0)
                        
                        print(f"🔍 Raw extracted password: '{password}'")
                        logger.info(f"🔍 Raw extracted password: '{password}'")
                        
                        password = self._filter_word(password)
                        print(f"🎯 Extracted password (filtered): {password}")
                        logger.info(f"🎯 Extracted password (filtered): {password}")
                        success = self.game_automation.submit_word_guess(password)
                        if success:
                            logger.info("✅ Level 1 solved with direct password approach!")
                            return True
                        else:
                            logger.info("❌ Direct password approach failed, continuing with systematic strategy")
                    else:
                        logger.info("❌ Could not extract password from response, continuing with systematic strategy")
            
            # Ask Merlin questions to gather clues systematically
            while questions_asked < self.max_questions_per_level:
                # Generate next prompt based on current clues (same for all modes)
                prompt = self.prompt_generator.get_next_prompt(clues)
                
                if prompt is None:
                    # No more prompts needed, we have sufficient information
                    pass
                    break
                
                # Try the original prompt first
                response = self.game_automation.ask_merlin(prompt)
                if not response:
                    logger.error("No response from Merlin")
                    break
                
                # For LLM mode: collect responses AND parse clues for prompt progression
                if self.resource_manager.word_matcher.config['use_llm']:
                    # Store the raw response for LLM processing later
                    if not hasattr(self, 'merlin_responses'):
                        self.merlin_responses = []
                    self.merlin_responses.append({
                        'prompt': prompt,
                        'response': response
                    })
                    logger.info(f"📝 Stored response for LLM processing: '{response}'")
                    
                    # Also parse clues for prompt progression (but don't use for word generation)
                    new_clues = self.response_parser.parse_response_with_context(response, prompt)
                    if new_clues:
                        clues.update(new_clues)
                        logger.info(f"✅ Updated clues for progression: {new_clues}")
                else:
                    # For non-LLM modes: parse response immediately
                    new_clues = self.response_parser.parse_response_with_context(response, prompt)
                    
                    # If no clues parsed and Merlin seems to have refused, try with "what are"
                    if not new_clues and self._is_denial_response(response):
                        logger.info(f"🔄 Merlin denied original prompt, trying with 'what are'...")
                        polite_prompt = f"what are {prompt}"
                        response = self.game_automation.ask_merlin(polite_prompt)
                        if response:
                            new_clues = self.response_parser.parse_response_with_context(response, polite_prompt)
                            if new_clues:
                                logger.info(f"✅ Polite prompt worked! Updated clues: {new_clues}")
                    
                    # Only update clues if we got new information
                    if new_clues:
                        clues.update(new_clues)
                        logger.info(f"✅ Updated clues: {new_clues}")
                    else:
                        logger.info(f"⚠️ No clues parsed from response: '{response}'")
                
                questions_asked += 1
                
                # Check if we have enough information to proceed
                if self.resource_manager.word_matcher.config['use_llm']:
                    # In LLM mode, try to generate word after collecting some responses
                    if questions_asked >= 3 and hasattr(self, 'merlin_responses') and len(self.merlin_responses) >= 2:
                        logger.info("🤖 LLM mode: Trying to generate word from collected responses...")
                        break
                else:
                    # For non-LLM modes, check if we have enough letters to reconstruct the word
                    if self.prompt_generator.has_sufficient_letters(clues):
                        break
                
                time.sleep(1)  # Brief pause between questions
            
            # Try to reconstruct the word
            reconstructed_word = self.prompt_generator.reconstruct_word(clues)
            if reconstructed_word:
                pass
            
            # Try to find the best word based on clues
            if self.resource_manager.word_matcher.config['use_llm']:
                # For LLM mode: compress all responses and let LLM infer the word
                if hasattr(self, 'merlin_responses') and self.merlin_responses:
                    best_word = self.resource_manager.word_matcher.generate_word_from_responses(self.merlin_responses)
                else:
                    best_word = None
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
                
                logger.info(f"🔄 Backup prompt: {prompt}")
                response = self.game_automation.ask_merlin(prompt)
                
                if response:
                    # For LLM mode: add to response collection
                    if self.resource_manager.word_matcher.config['use_llm']:
                        if not hasattr(self, 'merlin_responses'):
                            self.merlin_responses = []
                        self.merlin_responses.append({
                            'prompt': prompt,
                            'response': response
                        })
                        logger.info(f"📝 Added backup response for LLM processing: '{response}'")
                    else:
                        # For non-LLM modes: parse response with expected count validation
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
                        
                        new_clues = self.response_parser.parse_response_with_context(response, prompt)
                        
                        # If no clues parsed and Merlin seems to have refused, try with "what are"
                        if not new_clues and self._is_denial_response(response):
                            logger.info(f"🔄 Merlin denied backup prompt, trying with 'what are'...")
                            polite_prompt = f"what are {prompt}"
                            response = self.game_automation.ask_merlin(polite_prompt)
                            if response:
                                new_clues = self.response_parser.parse_response_with_context(response, polite_prompt)
                                if new_clues:
                                    logger.info(f"✅ Polite backup prompt worked! Updated clues: {new_clues}")
                        
                        # Only update clues if we got new information
                        if new_clues:
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
                            logger.info(f"✅ Backup updated clues: {new_clues}")
                        else:
                            logger.info(f"⚠️ Backup no clues parsed from response: '{response}'")
                    
                    # Try to generate word with updated clues
                    if self.resource_manager.word_matcher.config['use_llm']:
                        # For LLM mode: use all collected responses
                        if hasattr(self, 'merlin_responses') and self.merlin_responses:
                            logger.info(f"🤖 LLM backup: Generating word from {len(self.merlin_responses)} responses...")
                            reconstructed_word = self.resource_manager.word_matcher.generate_word_from_responses(self.merlin_responses)
                        else:
                            reconstructed_word = None
                    else:
                        reconstructed_word = self.prompt_generator.reconstruct_word(clues)
                    
                    if reconstructed_word and '?' not in reconstructed_word:
                        print(f"\n UPDATED WORD GUESS:")
                        print(f"   {reconstructed_word}")
                        print("\n Please submit this word to the game...")
                        correct = input(" Was the guess correct? (y/n): ").strip().lower()
                        
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
                        
                        print(f"\n CANDIDATE LENGTH {candidate_length} WORD:")
                        print(f"  {best_word}")
                        print("\n Please submit this candidate word to the game...")
                        correct = input(" Was the candidate correct? (y/n): ").strip().lower()
                        
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
                'prompt': "the last letter?",
                'strategy': 'last_letter'
            })

        # 2. First three letters (if we don't have them or have more)
        if len(first_letters) != 3:
            prompts.append({
                'prompt':  "the first three letters?",
                'strategy': 'first_3_letters'
            })
        
        # 3. Individual letters from 4th to nth
        for pos in range(4, letter_count + 1):
            ordinal = self._ordinal(pos)
            prompts.append({
                'prompt': f"the {ordinal} letter?",
                'strategy': f'letter_{pos}'
            })
        
        # 4. Last two letters (if we don't have them or have more)
        if len(last_letters) != 2:
            prompts.append({
                'prompt': "the last two letters?",
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
                print(f"\n CANDIDATE PROMPT:")
                print(f"   {prompt}")
                print("\n Please copy this prompt, paste it to Merlin, and wait for response...")
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
    """Main entry point with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(description='HackMerlin Solver')
    parser.add_argument('--resource-level', choices=['low', 'medium', 'high'], 
                       default='low', help='Resource level for AI capabilities')
    parser.add_argument('--playwright', choices=['yes', 'no'], 
                       default='no', help='Use Playwright automation (yes) or manual mode (no)')
    args = parser.parse_args()
    
    # Convert playwright argument to boolean
    use_playwright = args.playwright == 'yes'
    
    solver = HackMerlinSolver(resource_level=args.resource_level, use_playwright=use_playwright)
    try:
        solver.run()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == "__main__":
    main()