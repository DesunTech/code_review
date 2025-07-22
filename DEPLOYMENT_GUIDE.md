# 🚀 AI Code Reviewer Deployment Guide

This guide covers **both deployment patterns** for your vision:

1. **🔄 GitHub Actions** - Automatic code review on every push
2. **⚡ Standalone CLI Tool** - Easy installation for developers

## 🎯 Use Case 1: GitHub Actions (Automatic Reviews)

### Setup in 3 Steps

#### 1. Add GitHub Action to Your Repository
Copy the workflow file to `.github/workflows/ai-code-review.yml` in your repository:

```yaml
# This is already created as .github/workflows/ai-code-review.yml
# Just copy it to your target repositories
```

#### 2. Set Repository Secrets
Go to your repository → Settings → Secrets and Variables → Actions:

```bash
# Required: At least one AI provider
ANTHROPIC_API_KEY      # Claude API key (recommended)
OPENAI_API_KEY         # OpenAI API key (alternative)
OPENROUTER_API_KEY     # OpenRouter API key (cost-effective)

# Optional: GitHub token is automatically provided
GITHUB_TOKEN           # Auto-provided, no setup needed
```

#### 3. Test the Action
```bash
# Push code or create a pull request
git add .
git commit -m "feat: add new feature"
git push origin main

# The action will automatically:
# ✅ Detect language (JS/TS/Python/Go/Rust)
# ✅ Detect project type (React/Next.js/React Native/Node.js)
# ✅ Run AI code review
# ✅ Comment on PR with findings
# ✅ Set status checks
```

### What the Action Does

#### For React/Next.js/React Native Projects:
- **Auto-detects** project type from `package.json`
- **Identifies** TypeScript vs JavaScript
- **Reviews** code with framework-specific context
- **Comments** on PRs with actionable feedback

#### For Any Git Repository:
- **Triggers** on push to main/develop branches
- **Triggers** on pull requests
- **Analyzes** only changed files (efficient)
- **Provides** severity-based feedback
- **Fails** build for critical/major issues

#### Advanced Features:
- **Security scan** on `[security-scan]` commit message
- **Multi-provider fallback** (Claude → OpenAI → OpenRouter)
- **Artifact uploads** for detailed reports
- **Status checks** for build integration

---

## ⚡ Use Case 2: Standalone CLI Tool

Perfect for developers who want to use the tool without downloading the full Python codebase.

### 🔧 For Python Developers

#### Install via pip (Recommended)
```bash
# Install globally
pip install ai-code-reviewer

# Use immediately
ai-code-reviewer --base main --head HEAD --provider auto

# Or use shorter alias
code-review --list-providers
```

#### Install from Source
```bash
# Clone and install
git clone https://github.com/your-username/ai-code-reviewer.git
cd ai-code-reviewer
pip install -e .

# Use anywhere
ai-code-reviewer --help
```

### 📦 For Node.js/React/Next.js Developers

#### Using npx (Zero Installation)
```bash
# Use directly without installing anything
npx ai-code-reviewer --base main --head HEAD

# For React projects (auto-detected)
npx ai-code-reviewer --provider claude --output json

# For Next.js projects (auto-detected)
npx ai-code-reviewer --provider auto

# For React Native projects (auto-detected)
npx ai-code-reviewer --provider openai --fail-on major
```

#### Install Globally
```bash
# Install once, use everywhere
npm install -g ai-code-reviewer

# Use in any project
cd my-react-app
ai-code-reviewer --base main --head HEAD
```

### 🐳 Using Docker

#### Quick Run
```bash
# Run in current directory
docker run --rm -v $(pwd):/workspace \
  -e ANTHROPIC_API_KEY="your-key" \
  ai-code-reviewer/tool:latest \
  --base main --head HEAD

# With specific provider
docker run --rm -v $(pwd):/workspace \
  -e OPENAI_API_KEY="your-key" \
  ai-code-reviewer/tool:latest \
  --provider openai --output json
```

#### Build Your Own Image
```bash
# Build from source
docker build -t my-code-reviewer .

# Run
docker run --rm -v $(pwd):/workspace \
  -e ANTHROPIC_API_KEY="your-key" \
  my-code-reviewer \
  --provider auto
```

---

## 🔑 Provider Setup

### Quick Setup (Any Method)
```bash
# Choose your provider (pick at least one)
export ANTHROPIC_API_KEY="your-claude-key"        # Premium quality
export OPENAI_API_KEY="your-openai-key"           # Fast & reliable
export OPENROUTER_API_KEY="your-openrouter-key"   # Cost-effective
# Local models: Install Ollama + ollama pull codellama  # Free & private
```

### Team Environment Variables
```bash
# Add to your team's .bashrc/.zshrc
echo 'export ANTHROPIC_API_KEY="team-claude-key"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="team-openai-key"' >> ~/.bashrc

# Or use a .env file in your project
cat > .env << EOF
ANTHROPIC_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key
EOF
```

---

## 📋 Usage Examples for Different Teams

### React Team
```bash
# Manual review
npx ai-code-reviewer --provider auto --language typescript --project-type react

# In package.json scripts
{
  "scripts": {
    "review": "npx ai-code-reviewer --base main --head HEAD",
    "review:strict": "npx ai-code-reviewer --fail-on minor --provider claude"
  }
}

# GitHub Actions (automatic)
# Just add the workflow file - detects React automatically
```

### Next.js Team
```bash
# Manual review with Next.js context
npx ai-code-reviewer --provider claude --project-type nextjs

# Pre-commit hook
npx ai-code-reviewer --base HEAD~1 --head HEAD --fail-on major

# In package.json
{
  "scripts": {
    "review:pre-commit": "npx ai-code-reviewer --base HEAD~1 --head HEAD"
  }
}
```

### React Native Team
```bash
# Mobile-specific review
npx ai-code-reviewer --provider auto --project-type react-native

# Platform-specific
npx ai-code-reviewer --language typescript --project-type react-native --fail-on major

# GitHub Actions automatically detects React Native from package.json
```

### Python Team
```bash
# Install and use
pip install ai-code-reviewer
ai-code-reviewer --provider auto --language python

# In CI/CD
ai-code-reviewer --base main --head HEAD --fail-on critical
```

### Multi-Language Team
```bash
# Auto-detection works for any language
npx ai-code-reviewer --provider auto

# GitHub Actions handles:
# - JavaScript/TypeScript (React/Next.js/Node.js)
# - Python
# - Go
# - Rust
# - Java
```

---

## 🔄 CI/CD Integration Patterns

### GitHub Actions (Complete Setup)
1. Copy `.github/workflows/ai-code-review.yml` to your repo
2. Set repository secrets (API keys)
3. Push code - automatic reviews on every PR!

### GitLab CI
```yaml
ai-code-review:
  stage: test
  image: python:3.11
  script:
    - pip install ai-code-reviewer
    - ai-code-reviewer --base $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --head HEAD
  only:
    - merge_requests
  environment:
    name: review
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('AI Code Review') {
            steps {
                sh '''
                    pip install ai-code-reviewer
                    ai-code-reviewer --base origin/main --head HEAD --save-report review.json
                '''
                archiveArtifacts artifacts: 'review.json'
            }
        }
    }
}
```

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ai-code-review
        name: AI Code Review
        entry: npx ai-code-reviewer --base HEAD~1 --head HEAD --fail-on major
        language: system
        pass_filenames: false
```

---

## 📊 Distribution Strategy

### 1. PyPI Package (Python Developers)
```bash
# Publish to PyPI
python setup.py sdist bdist_wheel
twine upload dist/*

# Users install via:
pip install ai-code-reviewer
```

### 2. npm Package (Node.js Developers)
```bash
# Publish to npm
npm publish

# Users install via:
npm install -g ai-code-reviewer
# Or use directly: npx ai-code-reviewer
```

### 3. Docker Hub (Containerized)
```bash
# Build and publish
docker build -t ai-code-reviewer/tool:latest .
docker push ai-code-reviewer/tool:latest

# Users run via:
docker run ai-code-reviewer/tool:latest
```

### 4. GitHub Releases (Binary Distribution)
```bash
# Create releases with pre-built binaries
# Users download and run directly
```

---

## 🎯 Your Vision Achieved!

### ✅ Use Case 1: GitHub Actions
- **Zero Setup** for team members
- **Automatic** review on every push/PR
- **Framework Detection** (React/Next.js/React Native)
- **Intelligent Comments** on pull requests
- **Build Integration** with status checks

### ✅ Use Case 2: Standalone Tool
- **No Python Codebase** needed by developers
- **npx ai-code-reviewer** - works instantly
- **Framework Auto-Detection**
- **Multiple Installation Methods** (pip, npm, docker)
- **Team-Friendly** distribution

### 🚀 Ready for Production
Both deployment patterns are ready! Your team can:

1. **Set up GitHub Actions** once per repository
2. **Use npx/pip** for individual developer workflow
3. **Switch between providers** based on budget/quality needs
4. **Scale to any framework** (React, Next.js, React Native, Python, Go, etc.)

The system handles everything automatically - language detection, project type identification, provider fallback, and intelligent feedback! 🎉