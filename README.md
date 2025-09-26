# HackMerlin Solver

An autonomous solver for the HackMerlin game, supporting multiple strategies including LLM, embeddings, and rule-based approaches.

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser (for Playwright automation)

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
├── tests/                  # Test modules
├── scripts/               # Utility scripts
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Configuration

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```