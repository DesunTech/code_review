# AI Code Reviewer

An AI-powered code review system that analyzes git diffs using multiple AI providers (Claude, OpenAI, etc.) to detect performance, security, style, logic, and best practice issues. Generates reports and integrates with CI/CD pipelines like GitHub Actions.

## Features
- 🤖 **Multi-Provider AI Support** with automatic detection and intelligent fallback
  - Claude (Anthropic) - Premium quality
  - OpenAI (GPT-4) - Fast and reliable
  - OpenRouter - Cost-effective access to 20+ models
  - Local models (Ollama) - Private and free
- 🔄 **Intelligent Provider Selection** - Auto-detects available providers and falls back seamlessly
- 📊 **Git Integration** for diff fetching and analysis
- ⚙️ **Configurable Rules** - Severity thresholds, custom patterns, and language-specific rules
- 📋 **Multiple Report Formats** - Markdown, JSON with detailed findings and suggestions
- 🚀 **CI/CD Ready** - GitHub Actions, GitLab, Jenkins, pre-commit hooks
- 📈 **Provider Benchmarking** - Compare accuracy and performance across providers
- 🔧 **Extensible Architecture** - Custom analyzers, prompts, and integrations

## Quick Start

### 1. Setup (Virtual Environment)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AI Provider
Set up at least one AI provider:
```bash
# Option 1: Claude (Recommended)
export ANTHROPIC_API_KEY="your-claude-key"

# Option 2: OpenAI
export OPENAI_API_KEY="your-openai-key"

# Option 3: OpenRouter (Cost-effective)
export OPENROUTER_API_KEY="your-openrouter-key"

# Option 4: Local models (Free & Private)
# Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh
# ollama pull codellama
```

### 3. Run Code Review
```bash
# Auto-detect providers and review changes
python ai_code_reviewer.py --base main --head HEAD

# Specify provider and get JSON report
python ai_code_reviewer.py --provider claude --output json --save-report review.json

# List available providers
python ai_code_reviewer.py --list-providers
```

📖 **Detailed Setup**: See [PROVIDER_SETUP.md](PROVIDER_SETUP.md) for comprehensive provider configuration.

## Project Structure
- `ai_code_reviewer.py`: Core reviewer script with multi-provider support
- `multi_provider_integration.py`: Multi-AI provider support and benchmarking
- `config_manager.py`: Configuration loading and validation
- `demo_providers.py`: Interactive demo of multi-provider system
- `PROVIDER_SETUP.md`: Comprehensive provider setup guide
- `code-review-config.txt`: Sample configuration
- `setup-guide.md`: Detailed setup and usage guide

## Requirements
See `requirements.txt`.

## Contributing
Fork, create branch, add tests, submit PR. See setup-guide.md for more.

## TODO List

| Status     | Task                                                                 | Priority |
|------------|----------------------------------------------------------------------|----------|
| Completed | Create comprehensive documentation (README.md and setup-guide.md)    | High    |
| Completed | Add .env file template and virtual env setup instructions            | High    |
| Completed | Document and implement GitHub Action usage                           | High    |
| Pending   | Add unit/integration tests for core components                       | High    |
| Pending   | Implement caching for AI responses                                   | High    |
| Pending   | Expand multi-provider support (e.g., add Google Gemini)              | Medium  |
| Pending   | Add webhook integrations (e.g., Slack notifications)                 | Medium  |
| Pending   | Improve error handling (e.g., retries, alerts)                       | Medium  |
| Pending   | Optimize for large repos (e.g., split diffs)                         | Medium  |
| Pending   | Create a web UI for manual reviews                                   | Low     |
| Pending   | Add metrics dashboard for tracking findings                          | Low     |
| Pending   | Document contribution guidelines in README.md                        | Low     |
| Pending   | Audit for security (e.g., data leakage prevention)                   | Low     |

<!-- Security scan triggered at 2025-09-01 23:10:28 -->