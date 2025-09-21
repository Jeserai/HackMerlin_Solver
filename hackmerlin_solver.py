"""
HackMerlin Solver - AI Prompt Engineering Challenge with improved strategy.
"""
import logging
import time
from typing import Dict, Any
from game_automation import GameAutomation
from resource_manager import ResourceManager
from prompt_generator import PromptGenerator
from response_parser import ResponseParser
from config import MAX_QUESTIONS_PER_LEVEL, MAX_RETRIES_PER_LEVEL, RESOURCE_LEVELS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class HackMerlinSolver:
    """HackMerlin solver with improved letter extraction strategy."""
    
    def __init__(self, resource_level: str = 'low'):
        self.game_automation = GameAutomation()
        self.resource_manager = ResourceManager(resource_level)
        self.prompt_generator = PromptGenerator()
        self.response_parser = ResponseParser()
        self.current_level = 1
        self.max_levels = 6
        self.max_questions_per_level = MAX_QUESTIONS_PER_LEVEL
        self.max_retries_per_level = MAX_RETRIES_PER_LEVEL
        
        logger.info(f"HackMerlin Solver initialized with {resource_level} resources")
    
    def run(self) -> None:
        """Run the main game loop."""
        try:
            logger.info("Starting HackMerlin Solver")
            
            # Setup game automation
            self.game_automation.setup_driver()
            self.game_automation.navigate_to_game()
            
            # Main game loop
            while self.current_level <= self.max_levels:
                logger.info(f"Starting Level {self.current_level}")
                
                success = self._solve_level()
                
                if success:
                    logger.info(f"Successfully completed Level {self.current_level}")
                    self.current_level += 1
                    self.prompt_generator.reset()  # Reset for next level
                else:
                    logger.warning(f"Failed to solve Level {self.current_level}")
                    self.current_level += 1
                
                time.sleep(2)
            
            logger.info("Completed all target levels!")
            
        except Exception as e:
            logger.error(f"Error in main game loop: {e}")
            raise
        finally:
            self.game_automation.close()
    
    def _solve_level(self) -> bool:
        """Solve the current level using the improved strategy."""
        try:
            clues = {}
            questions_asked = 0
            
            # Ask Merlin questions to gather clues systematically
            while questions_asked < self.max_questions_per_level:
                # Generate next prompt based on current clues
                prompt = self.prompt_generator.get_next_prompt(clues)
                
                if prompt is None:
                    # No more prompts needed, we have sufficient information
                    logger.info("Have all necessary letters, attempting word guess")
                    break
                
                logger.info(f"Asking Merlin: {prompt}")
                
                # Ask Merlin and get response
                response = self.game_automation.ask_merlin(prompt)
                if not response:
                    logger.error("No response from Merlin")
                    break
                
                # Parse response to extract clues
                new_clues = self.response_parser.parse_response(response)
                clues.update(new_clues)
                
                logger.info(f"Current clues: {clues}")
                questions_asked += 1
                
                # Check if we have enough letters to reconstruct the word
                if self.prompt_generator.has_sufficient_letters(clues):
                    logger.info("Have sufficient letters, attempting word guess")
                    break
                
                time.sleep(1)  # Brief pause between questions
            
            # Try to reconstruct the word
            reconstructed_word = self.prompt_generator.reconstruct_word(clues)
            if reconstructed_word:
                logger.info(f"Reconstructed word: {reconstructed_word}")
            
            # Try to find the best word based on clues
            best_word = self.resource_manager.find_best_word(clues)
            if not best_word:
                logger.error("Failed to find a matching word")
                return False
            
            logger.info(f"Best word found: {best_word}")
            
            # Submit the word guess with retry logic
            success = self._submit_with_retry(best_word, clues)
            
            return success
            
        except Exception as e:
            logger.error(f"Error solving level: {e}")
            return False
    
    def _submit_with_retry(self, word: str, clues: Dict[str, Any]) -> bool:
        """Submit word guess with simple retry logic."""
        for attempt in range(self.max_retries_per_level):
            logger.info(f"Attempt {attempt + 1}: Submitting word '{word}'")
            
            # Submit the word guess
            success = self.game_automation.submit_word_guess(word)
            
            if success:
                logger.info(f"Successfully guessed word: {word}")
                return True
            
            logger.warning(f"Word '{word}' was incorrect, attempt {attempt + 1}")
            
            # For the first 6 levels, the systematic letter extraction strategy should work
            # If it fails, it's likely due to parsing errors or game interface issues
            if attempt < self.max_retries_per_level - 1:
                logger.info("The systematic letter extraction strategy should be sufficient for levels 1-6")
        
        logger.error(f"Failed to guess word after {self.max_retries_per_level} attempts")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='HackMerlin Solver')
    parser.add_argument('--level', type=int, help='Solve a specific level only')
    parser.add_argument('--max-levels', type=int, default=6,
                       help='Maximum number of levels to solve (default: 6)')
    parser.add_argument('--max-questions', type=int, default=MAX_QUESTIONS_PER_LEVEL,
                       help=f'Maximum questions per level (default: {MAX_QUESTIONS_PER_LEVEL})')
    parser.add_argument('--resource-level', choices=['low', 'medium', 'high'], default='low',
                       help='Resource level to use (default: low)')
    parser.add_argument('--max-retries', type=int, default=MAX_RETRIES_PER_LEVEL,
                       help=f'Maximum retries per level (default: {MAX_RETRIES_PER_LEVEL})')
    
    args = parser.parse_args()
    
    # Create solver instance
    solver = HackMerlinSolver(resource_level=args.resource_level)
    
    # Override settings if specified
    if args.max_levels:
        solver.max_levels = args.max_levels
    if args.max_questions:
        solver.max_questions_per_level = args.max_questions
    if args.max_retries:
        solver.max_retries_per_level = args.max_retries
    
    try:
        if args.level:
            # Solve single level
            solver.current_level = args.level
            solver.game_automation.setup_driver()
            solver.game_automation.navigate_to_game()
            success = solver._solve_level()
            solver.game_automation.close()
            print(f"Level {args.level} {'solved' if success else 'failed'}")
        else:
            # Solve all levels
            solver.run()
            print("All levels completed!")
    
    except KeyboardInterrupt:
        logger.info("Solver interrupted by user")
        print("Solver interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
