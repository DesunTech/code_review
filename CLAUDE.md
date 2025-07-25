# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Code Reviewer is a Python-based tool that provides AI-powered code review using multiple AI providers (Claude, OpenAI, OpenRouter, local models). It integrates with git to analyze diffs and generate detailed code review reports with findings on performance, security, style, logic, and best practices.

## Architecture

The codebase follows a modular architecture with these core components:

- **`ai_code_reviewer/ai_code_reviewer.py`**: Main CLI entry point and orchestration logic
- **`ai_code_reviewer/multi_provider_integration.py`**: Abstract provider system with implementations for different AI services
- **`ai_code_reviewer/config_manager.py`**: Configuration loading and validation
- **Provider Classes**: Each AI service (Claude, OpenAI, OpenRouter, Ollama) has its own provider class implementing the `AIProvider` interface

The system uses automatic provider detection based on available API keys and implements intelligent fallback between providers.

## Common Commands

### Development Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running the Tool
```bash
# Basic usage - auto-detect providers and review changes
python ai_code_reviewer.py --base main --head HEAD

# Specify provider and output format
python ai_code_reviewer.py --provider claude --output json --save-report review.json

# List available providers
python ai_code_reviewer.py --list-providers

# Run interactive provider demo
python demo_providers.py
```

### Testing and Quality
```bash
# Run tests (if implemented)
python -m pytest

# Run with development extras
pip install -e .[dev]

# Type checking
mypy ai_code_reviewer/

# Code formatting
black ai_code_reviewer/

# Linting
flake8 ai_code_reviewer/
```

### Package Management
```bash
# Build package
python setup.py sdist bdist_wheel

# Install from source
pip install -e .

# NPM wrapper commands
npm install
npm test
```

## Configuration

The tool supports multiple AI providers configured via environment variables:
- `ANTHROPIC_API_KEY` for Claude
- `OPENAI_API_KEY` for OpenAI
- `OPENROUTER_API_KEY` for OpenRouter
- Local Ollama models (no API key required)

Configuration file: `code-review-config.txt` (optional)

## Key Data Structures

- **`CodeReview`**: Dataclass representing individual findings with severity, category, file location, and suggestions
- **`ProviderConfig`**: Configuration object for AI provider settings
- **`AIProvider`**: Abstract base class for implementing new AI providers

## GitHub Actions Integration

The project includes portable GitHub Actions workflows in `PORTABLE_AI_CODE_REVIEW.yml` that can be copied to other repositories for CI/CD integration.