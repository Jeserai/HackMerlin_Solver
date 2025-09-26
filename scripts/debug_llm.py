#!/usr/bin/env python3
"""
Debug script for LLM parsing on GPU server
"""

import sys
import logging
sys.path.append('.')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_llm_parsing():
    """Test LLM parsing with detailed debugging."""
    print("🧪 Testing LLM Parsing on GPU Server")
    print("=" * 50)
    
    try:
        from resource_manager import ResourceManager
        print("✅ ResourceManager imported successfully")
        
        # Initialize high resource mode
        print("🚀 Initializing high resource mode...")
        rm = ResourceManager('high')
        print("✅ High resource mode initialized")
        
        # Test cases
        test_cases = [
            ("How many letters?", "Six letters, young one."),
            ("first four letters?", "The first four letters are ZODI."),
            ("last three letters?", "The password ends with \"LEE.\""),
        ]
        
        for prompt, response in test_cases:
            print(f"\n🔍 Testing: prompt='{prompt}', response='{response}'")
            
            # Test LLM parsing
            try:
                clues = rm.word_matcher.parse_response_with_llm(response, prompt)
                print(f"   LLM result: {clues}")
            except Exception as e:
                print(f"   LLM error: {e}")
            
            # Compare with regex parsing
            try:
                from response_parser import ResponseParser
                parser = ResponseParser()
                regex_clues = parser.parse_response_with_context(response, prompt)
                print(f"   Regex result: {regex_clues}")
            except Exception as e:
                print(f"   Regex error: {e}")
        
        print("\n🎉 LLM parsing test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_llm_generation():
    """Test LLM word generation."""
    print("\n🧪 Testing LLM Word Generation")
    print("=" * 50)
    
    try:
        from resource_manager import ResourceManager
        rm = ResourceManager('high')
        
        # Test word generation
        clues = {
            'letter_count': 6,
            'first_letters': 'basket',
            'last_letters': 'et'
        }
        
        print(f"🔍 Testing word generation with clues: {clues}")
        
        word = rm.word_matcher.generate_word_with_llm(clues)
        print(f"   Generated word: {word}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_parsing()
    test_llm_generation()
