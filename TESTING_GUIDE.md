# 🧪 Testing Guide: AI Code Reviewer with OpenRouter

## 🎯 Testing Both Use Cases with Your OpenRouter Key

### Prerequisites
- Your OpenRouter API key
- A separate codebase to test with
- Git repository with some code changes

---

## ⚡ Method 1: Test Standalone CLI Tool (Recommended)

### Step 1: Install the Tool
Choose one installation method:

#### Option A: Using pip (Python)
```bash
# Navigate to this project directory
cd /path/to/this/ai-code-reviewer

# Install from source
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

#### Option B: Using npx (Node.js - for React/Next.js projects)
```bash
# No installation needed - will auto-install
# Just run npx ai-code-reviewer in your test project
```

### Step 2: Set Your OpenRouter API Key
```bash
# Set the environment variable
export OPENROUTER_API_KEY="your-openrouter-api-key-here"

# Verify it's set
echo $OPENROUTER_API_KEY
```

### Step 3: Navigate to Your Test Codebase
```bash
# Go to your separate codebase
cd /path/to/your/test-project

# Make sure it's a git repository
git status
```

### Step 4: Run the Code Review
```bash
# Option A: If you installed via pip
ai-code-reviewer --provider openrouter --base main --head HEAD --list-providers

# Option B: If using npx (for Node.js projects)
npx ai-code-reviewer --provider openrouter --base main --head HEAD

# Option C: Run from source
python /path/to/ai-code-reviewer/ai_code_reviewer.py --provider openrouter --base main --head HEAD
```

### Step 5: Test Different Options
```bash
# Check available providers
ai-code-reviewer --list-providers

# Review with specific settings
ai-code-reviewer \
  --provider openrouter \
  --base main \
  --head HEAD \
  --language typescript \
  --project-type react \
  --output json \
  --save-report review.json

# Review last commit
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD
```

---

## 🔄 Method 2: Test GitHub Actions

### Step 1: Copy GitHub Action to Your Test Repository
```bash
# In your test codebase, create the workflow directory
mkdir -p .github/workflows

# Copy the workflow file
cp /path/to/ai-code-reviewer/.github/workflows/ai-code-review.yml .github/workflows/
```

### Step 2: Set Repository Secret
1. Go to your test repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `OPENROUTER_API_KEY`
5. Value: Your OpenRouter API key

### Step 3: Test the Action
```bash
# Make a test change and push
echo "console.log('test change');" >> test-file.js
git add .
git commit -m "test: trigger AI code review"
git push origin main

# Or create a pull request to test PR comments
git checkout -b test-branch
echo "const test = 'change';" >> another-file.js
git add .
git commit -m "feat: test PR review"
git push origin test-branch
# Then create PR on GitHub
```

---

## 🐳 Method 3: Test with Docker

### Step 1: Build Docker Image
```bash
# In the ai-code-reviewer directory
docker build -t test-ai-reviewer .
```

### Step 2: Run on Your Test Codebase
```bash
# Navigate to your test codebase
cd /path/to/your/test-project

# Run the review
docker run --rm \
  -v $(pwd):/workspace \
  -e OPENROUTER_API_KEY="your-openrouter-api-key" \
  test-ai-reviewer \
  --provider openrouter \
  --base main \
  --head HEAD
```

---

## 🔍 Quick Test Commands

### Test Provider Detection
```bash
# Check if OpenRouter is detected
export OPENROUTER_API_KEY="your-key"
ai-code-reviewer --list-providers

# Should show OpenRouter as available
```

### Test with Sample Code
```bash
# Create a test file with issues for review
cat > test-code.py << EOF
def bad_function(user_id):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    password = "hardcoded123"
    for i in range(len(user.purchases)):
        for j in range(len(user.purchases)):
            if user.purchases[i] > user.purchases[j]:
                print("found issue")
    return user
EOF

# Commit it
git add test-code.py
git commit -m "add test code with issues"

# Review it
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD
```

### Test Framework Detection
```bash
# If testing in a React/Next.js project
ai-code-reviewer --provider openrouter --base main --head HEAD
# Should auto-detect React/Next.js and provide framework-specific review

# If testing in a Python project
ai-code-reviewer --provider openrouter --language python --base main --head HEAD
```

---

## 📊 Expected Results

### Successful Test Should Show:
```bash
🔍 Available providers: openrouter
🎯 Primary provider: openrouter
🔄 Fallback providers:
✓ Loaded provider: openrouter
Using primary provider: openrouter

🤖 Analyzing code...
✅ Review completed! Found X issues:

1. CRITICAL - security
   📄 test-code.py (lines 2-2)
   💬 Potential SQL injection vulnerability...
   💡 Suggestion: Use parameterized queries...
```

### If OpenRouter Fails:
```bash
# Check your API key
echo $OPENROUTER_API_KEY

# Test API key directly
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -H "Content-Type: application/json" \
     https://openrouter.ai/api/v1/models
```

---

## 🛠 Troubleshooting

### Issue: "No providers available"
```bash
# Solution: Set the API key
export OPENROUTER_API_KEY="your-actual-key"
ai-code-reviewer --list-providers
```

### Issue: "OpenRouter API error"
```bash
# Check API key format
echo $OPENROUTER_API_KEY | wc -c  # Should be reasonable length

# Test with curl
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     "https://openrouter.ai/api/v1/models"
```

### Issue: "No changes to review"
```bash
# Make sure you have commits to compare
git log --oneline -5

# Or create a test change
echo "// test change" >> README.md
git add .
git commit -m "test change"
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD
```

### Issue: Module not found (when using pip install)
```bash
# Make sure you're in the right environment
source venv/bin/activate  # If using virtual env
pip install -e .  # Install in development mode
```

---

## 🎯 Quick Start Test Script

Create this test script in your test codebase:

```bash
#!/bin/bash
# test-ai-reviewer.sh

echo "🧪 Testing AI Code Reviewer with OpenRouter"

# Set API key (replace with your actual key)
export OPENROUTER_API_KEY="your-openrouter-api-key-here"

# Test 1: Check provider detection
echo "📍 Test 1: Provider Detection"
ai-code-reviewer --list-providers

# Test 2: Review last commit
echo "📍 Test 2: Review Last Commit"
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD

# Test 3: Review with specific options
echo "📍 Test 3: Full Review with Options"
ai-code-reviewer \
  --provider openrouter \
  --base main \
  --head HEAD \
  --output json \
  --save-report test-review.json

echo "✅ Testing complete! Check test-review.json for results."
```

Run it:
```bash
chmod +x test-ai-reviewer.sh
./test-ai-reviewer.sh
```

This should help you test both the standalone CLI and GitHub Actions with your OpenRouter key! Let me know which method you'd like to try first. 🚀