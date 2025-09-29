# HackMerlin Solver

An autonomous solver for the HackMerlin game, supporting multiple strategies including LLM, embeddings, and rule-based approaches.

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Playwright Browsers (for automation mode)

```bash
playwright install
```

### Resource Levels

- **Low**: Rule-based concatenation strategy
- **Medium**: Embeddings-based similarity search
- **High**: LLM-based inference (requires GPU or OpenAI API key)

### Modes

- **Manual Mode** (`--playwright no`): Copy-paste interactions with the game
- **Automation Mode** (`--playwright yes`): Automated browser interaction

## Project Structure

```
HackMerlin_Solver/
├── src/
│   └── hackmerlin/
│       ├── core/           # Core solving logic
│       │   ├── solver.py   # Main solver class
│       │   ├── game_automation.py
│       │   ├── prompt_generator.py
│       │   ├── response_parser.py
│       │   └── word_matcher.py
│       ├── ai/             # AI components
│       │   └── resource_manager.py
│       └── utils/          # Utilities
│           └── config.py
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Configuration

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Strategy

The HackMerlin Solver uses a multi-layered approach to solve word puzzles:

### 1. **Systematic Information Gathering**
- **Letter Count**: First asks "How many letters?" to determine word length
- **First Letters**: Extracts initial letters using "What are the first X letters?"
- **Last Letters**: Gets final letters with "What are the last X letters?"
- **Direct Password**: For Level 1, attempts direct "What is the password?" approach

### 2. **Intelligent Word Reconstruction**
- **Resource-Aware Matching**: Uses different strategies based on available resources:
  - **Low Resource**: Simple concatenation of known letters
  - **Medium Resource**: Embeddings-based similarity search for word completion
  - **High Resource**: LLM-powered inference for complex word reconstruction
- **Backup Strategies**: When primary approach fails, tries alternative prompts and word combinations

## Usage

```bash
python main.py --resource-level YOUR_CHOSEN_RESOURCE_LEVEL --playwright YES/NO
```