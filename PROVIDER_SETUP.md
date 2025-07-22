# AI Provider Setup Guide

The AI Code Review system now supports **automatic provider detection and intelligent fallback**! Here's how to set up each provider:

## 🎯 Quick Start

The system automatically detects available providers and selects the best one. Just set your API keys and run:

```bash
# Check what providers are available
python ai_code_reviewer.py --list-providers

# Use auto-detection (recommended)
python ai_code_reviewer.py --provider auto --base main --head HEAD

# Or specify a provider
python ai_code_reviewer.py --provider claude --base main --head HEAD
```

## 🔑 Provider Setup

### 1. Claude (Anthropic) - **Recommended**
**Best for:** Comprehensive code analysis, security reviews

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Test it
python ai_code_reviewer.py --provider claude --list-providers
```

**Get API Key:** https://console.anthropic.com/
- Sign up for Anthropic account
- Navigate to API Keys section
- Create new API key

### 2. OpenAI (GPT-4)
**Best for:** Fast reviews, good general analysis

```bash
# Set your API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Test it
python ai_code_reviewer.py --provider openai --list-providers
```

**Get API Key:** https://platform.openai.com/api-keys
- Sign up for OpenAI account
- Navigate to API Keys
- Create new secret key

### 3. OpenRouter - **Cost-Effective**
**Best for:** Access to multiple models with one API key

```bash
# Set your API key
export OPENROUTER_API_KEY="your-openrouter-api-key-here"

# Test it
python ai_code_reviewer.py --provider openrouter --list-providers
```

**Get API Key:** https://openrouter.ai/keys
- Sign up for OpenRouter account
- Generate API key
- Access 20+ different models including Claude, GPT-4, and others

### 4. Local Models (Ollama) - **Private & Free**
**Best for:** Private codebases, no internet required

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a code model
ollama pull codellama

# Or other options:
ollama pull llama2          # General purpose
ollama pull wizard-coder    # Code-focused
ollama pull deepseek-coder  # Advanced code model

# Set custom endpoint (optional)
export LOCAL_MODEL_ENDPOINT="http://localhost:11434/api/generate"

# Test it
python ai_code_reviewer.py --provider local --list-providers
```

## 🚀 Usage Examples

### Auto-Detection (Recommended)
```bash
# System automatically picks the best available provider
python ai_code_reviewer.py --base main --head HEAD
```

### Manual Provider Selection
```bash
# Use Claude as primary
python ai_code_reviewer.py --provider claude --base main --head HEAD

# Use OpenAI with OpenRouter fallback
python ai_code_reviewer.py --provider openai --fallback-providers openrouter local

# Use local model only (private codebases)
python ai_code_reviewer.py --provider local --base main --head HEAD
```

### Advanced Configuration
```bash
# Multiple fallbacks for maximum reliability
python ai_code_reviewer.py \
  --provider claude \
  --fallback-providers openai openrouter local \
  --language python \
  --project-type microservice \
  --fail-on major \
  --save-report review.json
```

## 🔄 Fallback Priority

The system uses this priority order when auto-detecting:

1. **Claude (Anthropic)** - Most comprehensive analysis
2. **OpenAI** - Fast and reliable
3. **OpenRouter** - Cost-effective, multiple models
4. **Local** - Private and free

## 💡 Pro Tips

### Environment Variables (.env file)
Create a `.env` file in your project root:

```env
# Primary providers
ANTHROPIC_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key

# Local model configuration
LOCAL_MODEL_ENDPOINT=http://localhost:11434/api/generate

# Optional: Model overrides
CLAUDE_MODEL=claude-3-opus-20240229
OPENAI_MODEL=gpt-4-turbo-preview
OPENROUTER_MODEL=anthropic/claude-3-opus
LOCAL_MODEL=codellama
```

### Cost Optimization
- **OpenRouter**: Cheapest option, access to multiple models
- **Local (Ollama)**: Completely free, great for private code
- **OpenAI**: Good balance of cost and performance
- **Claude**: Premium option, best quality

### Security Best Practices
```bash
# Use environment variables, not hardcoded keys
export ANTHROPIC_API_KEY="$(cat ~/.anthropic_key)"

# For CI/CD, use secrets management
# GitHub: Repository Settings > Secrets
# GitLab: Settings > CI/CD > Variables
# Jenkins: Credentials Plugin
```

## 🔧 Troubleshooting

### No Providers Available
```bash
❌ No AI providers available! Please set up at least one API key.

# Solution: Set at least one API key
export ANTHROPIC_API_KEY="your-key"
# OR
export OPENAI_API_KEY="your-key"
# OR install Ollama for local models
```

### Provider Failed
```bash
Primary provider failed: Invalid API key

# Solution: Check your API key
python ai_code_reviewer.py --list-providers

# The system will automatically try fallback providers
```

### Local Model Not Found
```bash
Local model error: model 'codellama' not found

# Solution: Pull the model
ollama pull codellama

# Or use a different model
export LOCAL_MODEL=llama2
```

## 📊 Provider Comparison

| Provider | Cost | Speed | Quality | Privacy | Setup |
|----------|------|-------|---------|---------|-------|
| Claude | $$$ | Medium | Excellent | Cloud | Easy |
| OpenAI | $$ | Fast | Good | Cloud | Easy |
| OpenRouter | $ | Fast | Good | Cloud | Easy |
| Local (Ollama) | Free | Slow | Good | Private | Medium |

## 🎮 Try the Demo

Run the interactive demo to see all providers in action:

```bash
python demo_providers.py
```

This will show:
- Provider auto-detection
- Manual selection
- Fallback functionality
- Sample code review

## 🚀 Ready for Production

The multi-provider system is now production-ready with:

✅ **Automatic provider detection**
✅ **Intelligent fallback support**
✅ **Manual provider selection**
✅ **Cost optimization options**
✅ **Private deployment support**
✅ **CI/CD integration ready**

Choose your providers based on your needs:
- **Maximum Quality**: Claude + OpenAI fallback
- **Cost Effective**: OpenRouter + Local fallback
- **Privacy First**: Local only
- **Best Reliability**: All providers with auto-fallback