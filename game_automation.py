"""
Game automation for HackMerlin - supports both Selenium and manual modes.
"""
import time
import logging
from typing import Optional, Dict, Any
from config import USE_SELENIUM, HEADLESS_MODE, GAME_URL

logger = logging.getLogger(__name__)


class GameAutomation:
    """Game automation supporting both Selenium and manual modes."""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.use_selenium = USE_SELENIUM
        self.manual_mode = not USE_SELENIUM
        
        if self.manual_mode:
            logger.info("Running in manual mode - copy/paste interactions")
        else:
            logger.info("Running in Selenium automation mode")
    
    def setup_driver(self) -> None:
        """Initialize the web driver if using Selenium."""
        if not self.use_selenium:
            return
            
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            if HEADLESS_MODE:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = webdriver.support.ui.WebDriverWait(self.driver, 10)
            
            logger.info("Web driver initialized")
        except Exception as e:
            logger.error(f"Failed to setup Selenium: {e}")
            logger.info("Falling back to manual mode")
            self.use_selenium = False
            self.manual_mode = True
    
    def navigate_to_game(self) -> None:
        """Navigate to the HackMerlin game."""
        if self.use_selenium:
            try:
                self.driver.get(GAME_URL)
                time.sleep(3)
                logger.info("Navigated to HackMerlin game")
            except Exception as e:
                logger.error(f"Failed to navigate: {e}")
                raise
        else:
            print(f"\n{'='*50}")
            print("MANUAL MODE ACTIVATED")
            print(f"Please navigate to: {GAME_URL}")
            print("Copy and paste prompts/responses as requested")
            print(f"{'='*50}\n")
    
    def ask_merlin(self, prompt: str) -> str:
        """Ask Merlin a question and get response."""
        try:
            if self.use_selenium:
                return self._ask_merlin_selenium(prompt)
            else:
                return self._ask_merlin_manual(prompt)
        except Exception as e:
            logger.error(f"Failed to ask Merlin: {e}")
            return ""
    
    def _ask_merlin_selenium(self, prompt: str) -> str:
        """Ask Merlin using Selenium automation."""
        try:
            # TODO: Find the actual input field and submit button
            # This needs to be adapted to the real game interface
            
            logger.info(f"Asking Merlin: {prompt}")
            
            # Simulate waiting for response
            time.sleep(2)
            
            # TODO: Extract actual response from Merlin
            # For now, return a simulated response based on the prompt
            response = self._simulate_merlin_response(prompt)
            
            logger.info(f"Merlin responds: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Selenium ask failed: {e}")
            return ""
    
    def _ask_merlin_manual(self, prompt: str) -> str:
        """Ask Merlin using manual copy/paste."""
        print(f"\n📝 PROMPT TO ASK MERLIN:")
        print(f"   {prompt}")
        print(f"\n⏳ Please copy this prompt, paste it to Merlin, and wait for response...")
        
        # Get response from user
        response = input(f"\n📥 MERLIN'S RESPONSE: ").strip()
        
        if not response:
            logger.warning("No response from the game")
            return ""
        
        logger.info(f"Merlin responds: {response}")
        return response
    
    def submit_word_guess(self, word: str) -> bool:
        """Submit a word guess to the game."""
        try:
            if self.use_selenium:
                return self._submit_word_selenium(word)
            else:
                return self._submit_word_manual(word)
        except Exception as e:
            logger.error(f"Failed to submit word: {e}")
            return False
    
    def _submit_word_selenium(self, word: str) -> bool:
        """Submit word using Selenium automation."""
        try:
            # TODO: Find actual word input field and submit button
            logger.info(f"Submitting word guess: {word}")
            
            # Simulate submission
            time.sleep(2)
            
            # TODO: Check if the guess is correct
            # For now, simulate success for demonstration
            return True
            
        except Exception as e:
            logger.error(f"Selenium submit failed: {e}")
            return False
    
    def _submit_word_manual(self, word: str) -> bool:
        """Submit word using manual input."""
        print(f"\n🎯 WORD GUESS:")
        print(f"   {word}")
        print(f"\n⏳ Please submit this word to the game...")
        
        # Get result from user
        result = input(f"\n✅ Was the guess correct? (y/n): ").strip().lower()
        
        success = result in ['y', 'yes', '1', 'true']
        logger.info(f"Word guess {'successful' if success else 'failed'}")
        return success
    
    def _simulate_merlin_response(self, prompt: str) -> str:
        """Simulate Merlin's response based on prompt type."""
        prompt_lower = prompt.lower()
        
        if "how many letters" in prompt_lower:
            return "The word has 5 letters."
        elif "first" in prompt_lower and "letters" in prompt_lower:
            return "The word starts with 'ap'."
        elif "last" in prompt_lower and "letters" in prompt_lower:
            return "The word ends with 'le'."
        elif "what is the 4th letter" in prompt_lower:
            return "The 4th letter is 'l'."
        elif "what is the 5th letter" in prompt_lower:
            return "The 5th letter is 'e'."
        elif "what" in prompt_lower and "letter" in prompt_lower:
            return "I can help you with questions about individual letters."
        else:
            return "I can help you with questions about the word's structure."
    
    def check_game_state(self) -> str:
        """Check current game state."""
        try:
            if self.use_selenium:
                # TODO: Check for level completion, game over, etc.
                return "playing"
            else:
                # In manual mode, assume we're always playing
                return "playing"
        except Exception as e:
            logger.error(f"Error checking game state: {e}")
            return "error"
    
    def get_current_level(self) -> int:
        """Get the current level number."""
        try:
            if self.use_selenium:
                # TODO: Extract level from game interface
                return 1
            else:
                # In manual mode, ask user
                try:
                    level = input(f"\n🎮 What level are you on? (default: 1): ").strip()
                    return int(level) if level else 1
                except ValueError:
                    return 1
        except Exception as e:
            logger.error(f"Error getting level: {e}")
            return 1
    
    def close(self) -> None:
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed")
        
        if self.manual_mode:
            print(f"\n{'='*50}")
            print("Manual mode session ended")
            print(f"{'='*50}\n")
