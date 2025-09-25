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
        self.current_level = 0  # Track current level (starts at 0)
        
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
                
                # Try with a shorter timeout first
                self.page.goto(GAME_URL, wait_until='domcontentloaded', timeout=15000)
                logger.info("✅ Page loaded, waiting for elements...")
                
                # Wait for key elements to be present with shorter timeout
                try:
                    self.page.wait_for_selector("textarea.m_8fb7ebe7.mantine-Input-input.mantine-Textarea-input", timeout=8000)
                    logger.info("✅ Game elements found")
                except Exception as selector_error:
                    logger.warning(f"Could not find textarea selector: {selector_error}")
                    # Try alternative selectors
                    try:
                        self.page.wait_for_selector("textarea", timeout=5000)
                        logger.info("✅ Found textarea with generic selector")
                    except Exception as generic_error:
                        logger.warning(f"Could not find any textarea: {generic_error}")
                        # Continue anyway, maybe the page is still loading
                
                logger.info(f"🌐 Successfully navigated to: {self.page.url}")
                logger.info("🎮 Game interface loaded and ready")
            except Exception as e:
                logger.error(f"Failed to navigate to game: {e}")
                logger.info("Falling back to manual mode")
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
            logger.info("🔍 Looking for textarea input field...")
            input_field = self.page.locator("textarea.m_8fb7ebe7.mantine-Input-input.mantine-Textarea-input")
            
            # Wait for input field to be visible
            input_field.wait_for(state="visible", timeout=5000)
            logger.info("✅ Input field found and visible")
            
            # Clear and fill the input
            input_field.clear()
            input_field.fill(prompt)
            logger.info("✅ Prompt entered into input field")
            
            # Find and click the Ask button (more specific selector)
            logger.info("🔍 Looking for Ask button...")
            ask_button = self.page.locator("button[type='submit']").first
            ask_button.wait_for(state="visible", timeout=5000)
            logger.info("✅ Ask button found and visible")
            
            ask_button.click()
            logger.info("✅ Ask button clicked")
            
            # Wait for response to appear
            logger.info("⏳ Waiting for Merlin's response...")
            self.page.wait_for_timeout(3000)
            
            # Extract response from blockquote
            logger.info("🔍 Looking for response blockquote...")
            blockquote = self.page.locator("blockquote.m_ddec01c0.mantine-Blockquote-root")
            response_element = blockquote.locator("p.mantine-focus-auto.m_b6d8b162.mantine-Text-root")
            
            # Wait for response element to be visible
            response_element.wait_for(state="visible", timeout=10000)
            response = response_element.text_content().strip()
            
            logger.info(f"✅ Merlin responds: {response}")
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
            
            # If no Continue button, check level progression
            try:
                # Check if we're on Instruction screen (indicates failure if no Continue button)
                try:
                    level_element = self.page.locator("h1.m_8a5d1357.mantine-Title-root").first
                    level_text = level_element.text_content().strip()
                    if "Instruction" in level_text:
                        logger.info(f"❌ Instruction screen detected without Continue button - word guess failed")
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
                            
                            logger.info(f"🔍 Page shows Level {page_level}, expected Level {expected_level}")
                            
                            if page_level == expected_level:
                                logger.info(f"✅ Level progressed from {self.current_level} to {page_level} - word guess successful")
                                self.current_level = page_level
                                return True
                            else:
                                logger.info(f"❌ Level did not progress as expected - word guess failed")
                                return False
                        except (ValueError, IndexError):
                            logger.warning(f"Could not parse level from: {level_text}")
                            return False
                    else:
                        logger.info(f"❌ No level information found - word guess failed")
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
                            # Increment level counter when Continue button is clicked
                            self.current_level += 1
                            logger.info(f"🎯 Level advanced to: {self.current_level}")
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
                # Use our tracked level counter
                logger.info(f"📊 Current tracked level: {self.current_level}")
                return self.current_level
            except Exception as e:
                logger.error(f"Error getting level: {e}")
                return self.current_level
        else:
            # In manual mode, always return 1 (no level detection)
            return 1
    
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