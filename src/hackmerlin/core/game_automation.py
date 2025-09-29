"""
Game automation for HackMerlin - supports both manual and Playwright modes.
"""
import time
import logging
import json
from typing import Optional, Dict, Any
from ..utils.config import GAME_URL, HEADLESS_MODE

logger = logging.getLogger(__name__)


class GameAutomation:
    """Game automation - supports both manual and Playwright modes."""
    
    def __init__(self, use_playwright: bool = False):
        self.use_playwright = use_playwright
        self.manual_mode = not use_playwright
        self.page = None
        self.browser = None
        self.context = None
        self.level_before_submit = None
        self.current_level = 0  # Track current level (starts at 0)
        
        pass
    
    def setup_driver(self) -> None:
        """Initialize Playwright if using automation."""
        if not self.use_playwright:
            return
            
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            
            # Launch browser with more stable settings
            self.browser = self.playwright.chromium.launch(
                headless=HEADLESS_MODE,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create context with more stable settings
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                ignore_https_errors=True
            )
            
            # Create page
            self.page = self.context.new_page()
            
            # Set longer timeouts
            self.page.set_default_timeout(30000)
            self.page.set_default_navigation_timeout(30000)
            
            pass
        except Exception as e:
            self.use_playwright = False
            self.manual_mode = True
    
    def navigate_to_game(self) -> None:
        """Navigate to the HackMerlin game."""
        if self.use_playwright:
            try:
                
                self.page.goto(GAME_URL, wait_until='domcontentloaded', timeout=15000)
                
                try:
                    self.page.wait_for_selector("textarea.m_8fb7ebe7.mantine-Input-input.mantine-Textarea-input", timeout=8000)
                except Exception as selector_error:
                    try:
                        self.page.wait_for_selector("textarea", timeout=5000)
                    except Exception as generic_error:
                        pass
                
                pass
            except Exception as e:
                self.use_playwright = False
                self.manual_mode = True
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
            return ""
    
    def _ask_merlin_manual(self, prompt: str) -> str:
        """Ask Merlin using manual copy/paste."""
        print(f"\nPROMPT TO ASK MERLIN:")
        print(f"   {prompt}")
        print(f"\nPlease copy this prompt, paste it to Merlin, and wait for response...")
        
        # Get response from user
        response = input(f"\nMERLIN'S RESPONSE: ").strip()
        
        if not response:
            return ""
        return response
    
    def _ask_merlin_playwright(self, prompt: str) -> str:
        """Ask Merlin using Playwright automation."""
        try:
            print(f"Asking Merlin: '{prompt}'")
            
            input_field = self.page.locator("textarea.m_8fb7ebe7.mantine-Input-input.mantine-Textarea-input")
            input_field.wait_for(state="visible", timeout=5000)
            
            input_field.clear()
            input_field.fill(prompt)
            
            ask_button = self.page.locator("button[type='submit']").first
            ask_button.wait_for(state="visible", timeout=5000)
            ask_button.click()
            
            self.page.wait_for_timeout(3000)
            
            blockquote = self.page.locator("blockquote.m_ddec01c0.mantine-Blockquote-root")
            response_element = blockquote.locator("p.mantine-focus-auto.m_b6d8b162.mantine-Text-root")
            response_element.wait_for(state="visible", timeout=10000)
            response = response_element.text_content().strip()
            return response
            
        except Exception as e:
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
            return False
    
    def _submit_word_manual(self, word: str) -> bool:
        """Submit word using manual input."""
        print(f"\nWORD GUESS:")
        print(f"   {word}")
        print(f"\nPlease submit this word to the game...")
        
        # Get result from user
        result = input(f"\nWas the guess correct? (y/n): ").strip().lower()
        
        success = result in ['y', 'yes', '1', 'true']
        if success:
            self.current_level += 1
        
        return success
    
    def _submit_word_playwright(self, word: str) -> bool:
        """Submit word using Playwright automation."""
        try:
            print(f"Submitting word: '{word}'")
            
            password_field = self.page.locator("input.m_8fb7ebe7.mantine-Input-input.mantine-TextInput-input")
            password_field.clear()
            password_field.fill(word)
            
            submit_button = self.page.locator("//button[.//span[contains(text(), 'Submit')]]")
            submit_button.click()
            
            self.page.wait_for_timeout(5000)
            
            continue_clicked = self._click_continue_button_if_present()
            
            if continue_clicked:
                return True
            
            # If no Continue button, check level progression
            try:
                # Check if we're on Instruction screen (indicates failure if no Continue button)
                try:
                    level_element = self.page.locator("h1.m_8a5d1357.mantine-Title-root").first
                    level_text = level_element.text_content().strip()
                    if "Instruction" in level_text:
                        pass
                        return False
                except:
                    pass
                
                # Check level progression using the page title
                try:
                    level_element = self.page.locator("h1.m_8a5d1357.mantine-Title-root").first
                    level_text = level_element.text_content().strip()
                    
                    if "Level" in level_text:
                        try:
                            page_level = int(level_text.split()[-1])
                            expected_level = self.current_level + 1
                            
                            pass
                            
                            if page_level == expected_level:
                                pass
                                self.current_level = page_level
                                return True
                            else:
                                pass
                                return False
                        except (ValueError, IndexError):
                            logger.warning(f"Could not parse level from: {level_text}")
                            return False
                    else:
                        pass
                        return False
                        
                except Exception as level_error:
                    logger.error(f"Error checking level progression: {level_error}")
                    return False
                    
            except Exception as e:
                logger.error(f"Error in success detection: {e}")
                return False
            
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
            pass
            
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
                    pass
                    
                    button = self.page.locator(selector)
                    if button.count() > 0:
                        button_text = button.text_content().strip()
                        
                        # Verify the button actually contains "Continue" text
                        if "Continue" not in button_text:
                            logger.warning(f"🔄 Button found but doesn't contain 'Continue' text: '{button_text}'")
                            continue  # Skip this button, try next selector
                        
                        pass
                        
                        if button.is_visible():
                            pass
                            button.click()
                            pass
                            # Increment level counter when Continue button is clicked
                            self.current_level += 1
                            pass
                            self.page.wait_for_timeout(2000)
                            return True
                        else:
                            pass
                            
                except Exception as e:
                    pass
                    continue
            
            # If no Continue button found, check if we're actually on a success page
            try:
                continue_elements = self.page.locator("//*[contains(text(), 'Continue')]")
                if continue_elements.count() > 0:
                    logger.warning(f"🔄 Found {continue_elements.count()} elements with 'Continue' text but couldn't click them")
                else:
                    pass
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
                # Use our tracked level counter
                logger.info(f"📊 Current tracked level: {self.current_level}")
                return self.current_level
            except Exception as e:
                logger.error(f"Error getting level: {e}")
                return self.current_level
        else:
            # In manual mode, return tracked level or assume starting at 0
            return self.current_level if hasattr(self, 'current_level') else 0
    
    def close(self) -> None:
        """Close the session."""
        if self.use_playwright:
            try:
                if self.browser:
                    self.browser.close()
                if hasattr(self, 'playwright') and self.playwright:
                    self.playwright.stop()
                logger.info("🚪 Playwright browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        else:
            print(f"\n{'='*50}")
            print("Manual mode session ended")
            print(f"{'='*50}\n")