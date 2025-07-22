# 🤖 OpenRouter Models Guide

## 🎯 **Current Default Model**

**Default Model**: `openai/gpt-4-turbo-preview`

This is configured in multiple places:

### **1. Code Configuration (multi_provider_integration.py:120)**
```python
"model": self.config.model or "openai/gpt-4-turbo-preview",
```

### **2. Default Config (config_manager.py:260)**
```python
"model": "openai/gpt-4-turbo-preview",
```

---

## 🔧 **How to Change the Model**

### **Method 1: Environment Variable (Easiest)**
```bash
# Set the model via environment variable
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"

# Then run your code review
ai-code-reviewer --provider openrouter --base main --head HEAD
```

### **Method 2: Create Custom Config File**
Create `config/code-review-config.json`:
```json
{
  "openrouter": {
    "model": "anthropic/claude-3.5-sonnet",
    "max_tokens": 4000,
    "temperature": 0.1
  }
}
```

### **Method 3: Modify the Default (Direct Code Change)**
Edit `ai_code_reviewer/multi_provider_integration.py`:
```python
# Line 120 - change from:
"model": self.config.model or "openai/gpt-4-turbo-preview",

# To your preferred model:
"model": self.config.model or "anthropic/claude-3.5-sonnet",
```

---

## 🌟 **Popular OpenRouter Models**

### **🏆 Best for Code Review:**

#### **Anthropic Models (Recommended)**
- `anthropic/claude-3.5-sonnet` - **Best overall**, excellent code analysis
- `anthropic/claude-3-opus` - Most capable, but slower
- `anthropic/claude-3-haiku` - Fastest, good for simple reviews

#### **OpenAI Models**
- `openai/gpt-4-turbo-preview` - **Current default**, solid performance
- `openai/gpt-4` - Reliable, slightly older
- `openai/gpt-4o` - Latest, optimized
- `openai/gpt-4o-mini` - Faster, cheaper

#### **Google Models**
- `google/gemini-pro-1.5` - Good for large codebases
- `google/gemini-flash-1.5` - Fast responses

#### **Meta Models**
- `meta-llama/llama-3.1-70b-instruct` - Open source, good performance
- `meta-llama/llama-3.1-8b-instruct` - Fastest, cheapest

### **💰 Cost Comparison (per 1M tokens)**
- `anthropic/claude-3-haiku`: ~$0.25 (cheapest)
- `openai/gpt-4o-mini`: ~$0.15 (very cheap)
- `openai/gpt-4-turbo-preview`: ~$10 (default)
- `anthropic/claude-3.5-sonnet`: ~$3 (good value)
- `anthropic/claude-3-opus`: ~$15 (most expensive)

---

## 🚀 **Quick Model Change Examples**

### **Change to Claude 3.5 Sonnet (Recommended)**
```bash
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"
ai-code-reviewer --provider openrouter --base main --head HEAD
```

### **Change to Cheaper Option (Haiku)**
```bash
export OPENROUTER_MODEL="anthropic/claude-3-haiku"
ai-code-reviewer --provider openrouter --base main --head HEAD
```

### **Change to Latest GPT-4**
```bash
export OPENROUTER_MODEL="openai/gpt-4o"
ai-code-reviewer --provider openrouter --base main --head HEAD
```

### **Change to Open Source (Llama)**
```bash
export OPENROUTER_MODEL="meta-llama/llama-3.1-70b-instruct"
ai-code-reviewer --provider openrouter --base main --head HEAD
```

---

## 📊 **Model Performance for Code Review**

### **🥇 Tier 1 (Best)**
- `anthropic/claude-3.5-sonnet` - Excellent at finding security issues
- `openai/gpt-4o` - Great overall analysis
- `anthropic/claude-3-opus` - Most thorough reviews

### **🥈 Tier 2 (Good)**
- `openai/gpt-4-turbo-preview` - Current default, reliable
- `google/gemini-pro-1.5` - Good with large files
- `anthropic/claude-3-sonnet` - Solid performance

### **🥉 Tier 3 (Fast/Cheap)**
- `anthropic/claude-3-haiku` - Quick reviews
- `openai/gpt-4o-mini` - Budget-friendly
- `meta-llama/llama-3.1-70b-instruct` - Open source option

---

## 🔧 **Advanced Configuration**

### **Create a Custom Config File**
`config/openrouter-models.json`:
```json
{
  "development": {
    "model": "anthropic/claude-3-haiku",
    "max_tokens": 2000,
    "temperature": 0.1
  },
  "production": {
    "model": "anthropic/claude-3.5-sonnet",
    "max_tokens": 4000,
    "temperature": 0.0
  },
  "security-focused": {
    "model": "anthropic/claude-3-opus",
    "max_tokens": 6000,
    "temperature": 0.0
  }
}
```

### **Use Different Models for Different Review Types**
```bash
# For security reviews (most thorough)
export OPENROUTER_MODEL="anthropic/claude-3-opus"
ai-code-reviewer --provider openrouter --project-type security-focused

# For quick PR reviews (fast)
export OPENROUTER_MODEL="anthropic/claude-3-haiku"
ai-code-reviewer --provider openrouter --fail-on major

# For comprehensive reviews (balanced)
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"
ai-code-reviewer --provider openrouter --output json
```

---

## 🐙 **For GitHub Actions**

### **Set Model in Repository Secrets**
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Add new secret:
   - **Name**: `OPENROUTER_MODEL`
   - **Value**: `anthropic/claude-3.5-sonnet`

### **Update GitHub Workflow**
Edit `.github/workflows/ai-code-review.yml`:
```yaml
- name: Run AI Code Review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    OPENROUTER_MODEL: ${{ secrets.OPENROUTER_MODEL }}  # Add this line
  run: |
    ai-code-reviewer \
      --provider openrouter \
      --base ${{ steps.changed-files.outputs.base_sha }} \
      --head ${{ steps.changed-files.outputs.head_sha }}
```

---

## 🧪 **Test Different Models**

### **Quick Test Script**
```bash
#!/bin/bash
# test-models.sh

models=(
    "anthropic/claude-3.5-sonnet"
    "openai/gpt-4o"
    "anthropic/claude-3-haiku"
    "meta-llama/llama-3.1-70b-instruct"
)

for model in "${models[@]}"; do
    echo "🤖 Testing model: $model"
    export OPENROUTER_MODEL="$model"
    ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD
    echo "---"
done
```

### **Compare Results**
```bash
# Test with current default
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD --save-report gpt4-results.json

# Test with Claude 3.5 Sonnet
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD --save-report claude-results.json

# Compare the results
echo "GPT-4 found: $(jq length gpt4-results.json) issues"
echo "Claude found: $(jq length claude-results.json) issues"
```

---

## 💡 **My Recommendations**

### **For Most Users:**
```bash
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"
```
**Why:** Best balance of quality, speed, and cost

### **For Budget-Conscious:**
```bash
export OPENROUTER_MODEL="anthropic/claude-3-haiku"
```
**Why:** Fast and cheap, still good quality

### **For Critical Security Reviews:**
```bash
export OPENROUTER_MODEL="anthropic/claude-3-opus"
```
**Why:** Most thorough analysis, best for security

### **For Large Codebases:**
```bash
export OPENROUTER_MODEL="google/gemini-pro-1.5"
```
**Why:** Handles large contexts well

---

## 🔍 **How to Check What Model is Being Used**

Add this to see which model is active:
```bash
ai-code-reviewer --provider openrouter --list-providers
echo "Active model: $OPENROUTER_MODEL"
```

The tool will show you exactly which model it's using in the output! 🚀