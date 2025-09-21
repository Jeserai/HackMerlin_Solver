# HackMerlin Solver

An autonomous agent that can play the HackMerlin AI prompt engineering challenge (https://hackmerlin.io/) with improved letter extraction strategy.

## Game Understanding

HackMerlin is an AI prompt engineering challenge where:
1. **You ask Merlin (an AI) questions** to get clues about a secret word
2. **Merlin responds with information** about the word's structure/characteristics  
3. **You use the clues to guess the word** and advance to the next level
4. **The challenge is in crafting effective prompts** to extract useful information

## Key Improvements

### 1. **Systematic Letter Extraction**
- Gets letter count first
- Extracts first few letters and last few letters
- **Asks for individual letters at missing positions** (e.g., "What is the 4th letter?")
- **Reconstructs word by concatenating all letters directly**

### 2. **Resource-Based Strategies**
- **Low Resources**: Direct letter concatenation (most efficient)
- **Medium Resources**: Word embeddings for similarity search
- **High Resources**: LLM prediction (OpenAI GPT or HuggingFace models)

### 3. **Optional Automation**
- **Selenium Mode**: Full browser automation (default)
- **Manual Mode**: Copy/paste prompts and responses (set `USE_SELENIUM=false`)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up API keys:
```bash
cp env_example.txt .env
# Edit .env with your API keys for high-resource features
```

3. Make sure Chrome is installed (for Selenium mode)

## Usage

### Basic Usage
```bash
# Low resources (direct concatenation)
python hackmerlin_solver.py

# High resources (LLM + embeddings)
python hackmerlin_solver.py --resource-level high

# Manual mode (copy/paste)
# Set USE_SELENIUM=false in config.py
python hackmerlin_solver.py
```

### Advanced Usage
```bash
# Solve specific level with retry logic
python hackmerlin_solver.py --level 3 --max-retries 5

# Use medium resources (embeddings only)
python hackmerlin_solver.py --resource-level medium

# Limit questions per level
python hackmerlin_solver.py --max-questions 3
```

### Command Line Options
- `--level`: Solve a specific level only (for testing)
- `--max-levels`: Maximum number of levels to solve (default: 6)
- `--max-questions`: Maximum questions to ask Merlin per level (default: 10)
- `--resource-level`: Choose 'low', 'medium', or 'high' (default: low)
- `--max-retries`: Maximum retries per level (default: 3)

## Strategy

The solver follows this proven strategy for the first 6 levels:

1. **Ask Systematic Questions**: 
   - "How many letters?" → Get letter count (n)
   - "What are the first 3 letters?" → Get first a letters
   - "What are the last 3 letters?" → Get last b letters
   - "What is the 4th letter?" → Get individual letters for positions a+1 to n-b-1

2. **Reconstruct Word Directly**: 
   - **Low Resources**: Concatenate all letters: `first_letters + middle_letters + last_letters`
   - **Medium Resources**: Use embeddings to find similar words
   - **High Resources**: Use LLM to predict from clues


## Configuration

Edit `config.py` to customize:
- Resource levels and strategies
- Automation settings (Selenium vs manual)
- API keys for LLM/embeddings
- Game settings (timeouts, retries)

## Project Structure
```
HackMerlin_Solver/
├── hackmerlin_solver.py      # Main solver with improved strategy
├── game_automation.py        # Selenium + manual modes
├── prompt_generator.py       # Systematic letter extraction
├── response_parser.py        # Parses individual letter positions
├── word_matcher.py           # Direct concatenation + LLM/embeddings
├── resource_manager.py       # Resource level management
├── config.py                 # Configuration settings
├── requirements.txt          # Dependencies
├── env_example.txt           # API key template
└── README.md                 # This file
```

## Resource Levels

### Low Resources (Default)
- **Strategy**: Direct letter concatenation
- **Dependencies**: Minimal (just selenium, requests)
- **Speed**: Fastest
- **Accuracy**: High (if all letters extracted correctly)

### Medium Resources
- **Strategy**: Word embeddings (Word2Vec)
- **Dependencies**: gensim
- **Speed**: Medium
- **Accuracy**: Good (finds similar words)

### High Resources
- **Strategy**: LLM prediction + embeddings
- **Dependencies**: openai (optional), transformers
- **Speed**: Slower
- **Accuracy**: Best (but may overthink simple cases)
- **Note**: Uses local HuggingFace models (no API key needed)

## Implementation Notes

- **Placeholder Game Interface**: Currently has simulated responses - adapt to real game interface
- **Systematic Approach**: Extracts ALL individual letters when possible
- **Fallback Mechanisms**: Multiple strategies ensure solver always works
- **Modular Design**: Easy to extend with new strategies or automation modes

## License

This project is for educational purposes. Please respect the game's terms of service.
