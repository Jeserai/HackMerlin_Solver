"""
Game automation for HackMerlin - supports both manual and Playwright modes.
"""
import time
import logging
import json
from typing import Optional, Dict, Any
from config import GAME_URL, USE_SELENIUM, HEADLESS_MODE

logger = logging.getLogger(__name__)


class GameAutomation:
    """Game automation - supports both manual and Playwright modes."""
    
    def __init__(self):
        self.use_playwright = USE_SELENIUM  # Using same config flag for now
        self.manual_mode = not USE_SELENIUM
        self.page = None
        self.browser = None
        self.context = None
        self.level_before_submit = None
        
        if self.manual_mode:
            logger.info("Running in manual mode - copy/paste interactions")
        else:
            logger.info("Running in Playwright automation mode")
    
    def setup_driver(self) -> None:
        """Initialize Playwright if using automation."""
        if not self.use_playwright:
            return
            
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            
            # Launch browser
            self.browser = playwright.chromium.launch(
                headless=HEADLESS_MODE,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions'
                ]
            )
            
            # Create context
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            
            # Create page
            self.page = self.context.new_page()
            
            logger.info("🚀 Playwright browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup Playwright: {e}")
            logger.info("Falling back to manual mode")
            self.use_playwright = False
            self.manual_mode = True
    
    def navigate_to_game(self) -> None:
        """Navigate to the HackMerlin game."""
        if self.use_playwright:
            try:
                logger.info("🌐 Navigating to HackMerlin game...")
                self.page.goto(GAME_URL)
                self.page.wait_for_load_state('networkidle')
                logger.info(f"🌐 Successfully navigated to: {self.page.url}")
            except Exception as e:
                logger.error(f"Failed to navigate to game: {e}")
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
            if self.use_playwright:
                return self._ask_merlin_playwright(prompt)
            else:
                return self._ask_merlin_manual(prompt)
        except Exception as e:
            logger.error(f"Failed to ask Merlin: {e}")
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
    
    def _ask_merlin_playwright(self, prompt: str) -> str:
        """Ask Merlin using Playwright automation."""
        try:
            print(f"🤖 Asking Merlin: '{prompt}'")
            logger.info(f"🤖 Asking Merlin: '{prompt}'")
            
            # Find and clear the textarea input field
            input_field = self.page.locator("textarea.m_8fb7ebe7.mantine-Input-input.mantine-Textarea-input")
            input_field.clear()
            input_field.fill(prompt)
            
            # Find and click the Ask button
            ask_button = self.page.locator("button[type='submit']")
            ask_button.click()
            
            # Wait for response
            self.page.wait_for_timeout(2000)
            
            # Extract response from blockquote
            blockquote = self.page.locator("blockquote.m_ddec01c0.mantine-Blockquote-root")
            response_element = blockquote.locator("p.mantine-focus-auto.m_b6d8b162.mantine-Text-root")
            response = response_element.text_content().strip()
            
            logger.info(f"Merlin responds: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Playwright ask failed: {e}")
            # Fall back to manual mode if Playwright fails
            logger.info("Falling back to manual mode")
            self.use_playwright = False
            self.manual_mode = True
            return self._ask_merlin_manual(prompt)
    
    def submit_word_guess(self, word: str) -> bool:
        """Submit a word guess to the game."""
        try:
            if self.use_playwright:
                # Store current level before submission
                try:
                    self.level_before_submit = self.get_current_level()
                    logger.info(f"Stored level before submission: {self.level_before_submit}")
                except Exception as e:
                    logger.warning(f"Could not get current level: {e}")
                    self.level_before_submit = None
                
                return self._submit_word_playwright(word)
            else:
                return self._submit_word_manual(word)
        except Exception as e:
            logger.error(f"Failed to submit word: {e}")
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
    
    def _submit_word_playwright(self, word: str) -> bool:
        """Submit word using Playwright automation."""
        try:
            print(f"🎯 Submitting word: '{word}'")
            logger.info(f"🎯 Submitting word: '{word}'")
            
            # Find the password input field
            password_field = self.page.locator("input.m_8fb7ebe7.mantine-Input-input.mantine-TextInput-input")
            password_field.clear()
            password_field.fill(word)
            
            # Find and click the Submit button (for password submission)
            submit_button = self.page.locator("//button[.//span[contains(text(), 'Submit')]]")
            submit_button.click()
            
            # Wait and check for Continue button first
            logger.info("⏳ Waiting 5 seconds to check for Continue button...")
            self.page.wait_for_timeout(5000)
            
            # Check for Continue button after every submission
            print("🔄 Checking for Continue button after submission...")
            logger.info("🔄 Checking for Continue button after submission...")
            continue_clicked = self._click_continue_button_if_present()
            
            if continue_clicked:
                print("✅ Continue button clicked - word guess successful")
                logger.info("✅ Continue button clicked - word guess successful")
                return True
            
            # If no Continue button, check level change or Instruction screen
            try:
                current_level = self.get_current_level()
                
                # Check if we're on Instruction screen (indicates success)
                try:
                    level_element = self.page.locator("h1.m_8a5d1357.mantine-Title-root")
                    level_text = level_element.text_content().strip()
                    if "Instruction" in level_text:
                        logger.info(f"✅ Instruction screen detected - word guess successful")
                        return True
                except:
                    pass
                
                # Check level change
                success = self.level_before_submit and current_level > self.level_before_submit
                
                if success:
                    logger.info(f"✅ Level changed: {self.level_before_submit} → {current_level} - word guess successful")
                    return True
                else:
                    logger.info("❌ Level did not change - word guess failed")
                    return False
            except Exception as e:
                logger.error(f"Error checking level change: {e}")
                return continue_clicked  # Return True if Continue was clicked
            
        except Exception as e:
            logger.error(f"Playwright submit failed: {e}")
            # Fall back to manual mode if Playwright fails
            logger.info("Falling back to manual mode")
            self.use_playwright = False
            self.manual_mode = True
            return self._submit_word_manual(word)
    
    def check_game_state(self) -> str:
        """Check current game state."""
        return "playing"
    
    def _click_continue_button_if_present(self) -> bool:
        """Click the Continue button if it appears after successful level completion."""
        try:
            logger.info("🔄 Checking for Continue button...")
            
            # Wait a bit for the Continue button to appear
            self.page.wait_for_timeout(2000)
            
            # Look for Continue button with exact selectors - MUST contain "Continue" text
            continue_selectors = [
                "//button[.//span[contains(text(), 'Continue')]]",  # XPath for span with Continue text
                "//button[contains(text(), 'Continue')]",  # XPath for button with Continue text
                "//button[.//span[text()='Continue']]",  # Exact text match
                "//button[text()='Continue']"  # Direct button text
            ]
            
            for i, selector in enumerate(continue_selectors):
                try:
                    logger.info(f"🔄 Trying Continue button selector {i+1}: {selector}")
                    
                    button = self.page.locator(selector)
                    if button.count() > 0:
                        button_text = button.text_content().strip()
                        
                        # Verify the button actually contains "Continue" text
                        if "Continue" not in button_text:
                            logger.warning(f"🔄 Button found but doesn't contain 'Continue' text: '{button_text}'")
                            continue  # Skip this button, try next selector
                        
                        logger.info(f"🔄 Button text verified: '{button_text}'")
                        
                        if button.is_visible():
                            logger.info("🔄 Continue button found and visible, clicking it...")
                            button.click()
                            logger.info("🔄 Continue button clicked successfully")
                            self.page.wait_for_timeout(2000)
                            return True
                        else:
                            logger.info("🔄 Button found but not visible")
                            
                except Exception as e:
                    logger.info(f"🔄 Selector {i+1} failed: {e}")
                    continue
            
            # If no Continue button found, check if we're actually on a success page
            try:
                continue_elements = self.page.locator("//*[contains(text(), 'Continue')]")
                if continue_elements.count() > 0:
                    logger.warning(f"🔄 Found {continue_elements.count()} elements with 'Continue' text but couldn't click them")
                else:
                    logger.info("🔄 No Continue button found - this level may not have one")
            except Exception as e:
                logger.warning(f"🔄 Error checking for Continue elements: {e}")
            
            return False
            
        except Exception as e:
            logger.warning(f"Error looking for Continue button: {e}")
            return False
    
    def get_current_level(self) -> int:
        """Get the current level number."""
        if self.use_playwright:
            try:
                # Find the level header
                level_element = self.page.locator("h1.m_8a5d1357.mantine-Title-root")
                level_text = level_element.text_content().strip()
                
                # Extract number from "Level X" text
                if "Level" in level_text:
                    try:
                        level_num = int(level_text.split()[-1])
                        logger.info(f"📊 Current level: {level_num}")
                        return level_num
                    except (ValueError, IndexError):
                        logger.warning(f"Could not parse level from: {level_text}")
                        return 1
                elif "Instruction" in level_text:
                    # Instruction screen appears after successful level completion
                    logger.info(f"📊 Instruction screen detected: {level_text} (indicates success)")
                    return self.level_before_submit + 1 if self.level_before_submit else 1
                else:
                    logger.warning(f"Unexpected level format: {level_text}")
                    return 1
            except Exception as e:
                logger.error(f"Error getting level: {e}")
                return 1
        else:
            # In manual mode, always return 1 (no level detection)
            return 1
    
    def close(self) -> None:
        """Close the session."""
        if self.use_playwright and self.browser:
            try:
                self.browser.close()
                logger.info("🚪 Playwright browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        else:
            print(f"\n{'='*50}")
            print("Manual mode session ended")
            print(f"{'='*50}\n")