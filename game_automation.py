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
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            
            logger.info(f"Asking Merlin: {prompt}")
            
            # Find the textarea input field for asking questions
            input_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='You can talk to merlin here...']"))
            )
            
            # Clear and type the prompt
            input_field.clear()
            input_field.send_keys(prompt)
            
            # Find and click the Ask button
            ask_button = self.driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Ask')]]")
            ask_button.click()
            
            # Wait for Merlin's response to appear
            time.sleep(3)
            
            # Extract response from the blockquote area
            response_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "blockquote.mantine-Blockquote-root p"))
            )
            
            response = response_element.text.strip()
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
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            
            logger.info(f"Submitting word guess: {word}")
            
            # Find the password input field
            password_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='SECRET PASSWORD']"))
            )
            
            # Clear and type the word
            password_field.clear()
            password_field.send_keys(word)
            
            # Find and click the Submit button
            submit_button = self.driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Submit')]]")
            submit_button.click()
            
            # Wait for response
            time.sleep(3)
            
            # Check if we got a success message or moved to next level
            # For now, we'll need to check the page for success indicators
            # This might need adjustment based on how the game shows success/failure
            try:
                # Look for level change or success message
                level_element = self.driver.find_element(By.CSS_SELECTOR, "h1.mantine-Title-root")
                current_level = level_element.text
                logger.info(f"Current level after submission: {current_level}")
                
                # If we're still on the same level, the guess was likely wrong
                # This is a basic check - might need refinement
                return "Level" in current_level
                
            except:
                # If we can't find level info, assume success for now
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
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support import expected_conditions as EC
                
                # Extract level from the h1 element
                level_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.mantine-Title-root"))
                )
                level_text = level_element.text.strip()
                
                # Extract number from "Level X" text
                if "Level" in level_text:
                    try:
                        level_num = int(level_text.split()[-1])
                        return level_num
                    except (ValueError, IndexError):
                        logger.warning(f"Could not parse level from: {level_text}")
                        return 1
                else:
                    logger.warning(f"Unexpected level format: {level_text}")
                    return 1
            else:
                # In manual mode, always return 1 (no level detection)
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
