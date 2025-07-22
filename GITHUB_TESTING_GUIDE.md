# 🐙 GitHub Testing Guide for AI Code Reviewer

## 🎯 **Two Ways to Test on GitHub**

### **Method 1: Test on Your Separate Repository (Recommended)**
### **Method 2: Test on This Repository**

---

## 🚀 **Method 1: Test on Your Separate Repository**

### **Step 1: Copy the GitHub Action File**
```bash
# Go to your separate codebase
cd /path/to/your/separate/project

# Create the workflow directory
mkdir -p .github/workflows

# Copy the workflow file from this project
cp /Users/desuntechnology/Desktop/tools/code_review/.github/workflows/ai-code-review.yml .github/workflows/
```

### **Step 2: Set Up Repository Secret**
1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `OPENROUTER_API_KEY`
6. Value: Your actual OpenRouter API key
7. Click **Add secret**

### **Step 3: Test the Action**

#### **Option A: Test with Push to Main**
```bash
# Make a small change to trigger the action
echo "// Test change for AI review" >> README.md
git add .
git commit -m "test: trigger AI code review"
git push origin main
```

#### **Option B: Test with Pull Request (Better)**
```bash
# Create a test branch
git checkout -b test-ai-review

# Make some changes with intentional issues
cat > test-file.js << 'EOF'
function badFunction(userId) {
    // SQL injection vulnerability
    const query = "SELECT * FROM users WHERE id = " + userId;

    // Hardcoded password
    const password = "hardcoded123";

    // Inefficient loop
    for (let i = 0; i < users.length; i++) {
        for (let j = 0; j < users.length; j++) {
            if (users[i].id === users[j].id) {
                console.log("duplicate found");
            }
        }
    }

    return query;
}
EOF

git add .
git commit -m "feat: add test function with issues"
git push origin test-ai-review
```

Then create a Pull Request on GitHub.

### **Step 4: Check the Results**
1. Go to **Actions** tab in your repository
2. You should see "AI Code Review" workflow running
3. Click on it to see the progress
4. If testing with PR, check the PR for AI comments

---

## 🧪 **Method 2: Test on This Repository**

### **Step 1: Add Your OpenRouter Key Here**
```bash
# Go to this repository on GitHub:
# https://github.com/your-username/code_review (or wherever you put this)

# Add secret: OPENROUTER_API_KEY with your key
```

### **Step 2: Create a Test Branch**
```bash
# In this directory
git checkout -b test-openrouter-review

# Create a test file with issues
cat > test-review.py << 'EOF'
def vulnerable_function(user_input):
    # SQL injection risk
    query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # Hardcoded secret
    api_key = "sk-1234567890abcdef"

    # Poor error handling
    try:
        result = execute_query(query)
    except:
        pass

    # Inefficient algorithm
    numbers = [1, 2, 3, 4, 5] * 1000
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if numbers[i] == numbers[j]:
                print("found match")

    return result
EOF

git add .
git commit -m "test: add code with security and performance issues"
git push origin test-openrouter-review
```

### **Step 3: Create Pull Request**
1. Go to GitHub and create PR from `test-openrouter-review` to `main`
2. The AI Code Review action should trigger automatically

---

## 📊 **What You Should See**

### **Successful GitHub Action Run:**
```
🔍 Available providers: openrouter
🎯 Primary provider: openrouter
✓ Loaded provider: openrouter
Using primary provider: openrouter

🤖 Analyzing code...
✅ Review completed! Found 5 issues:

1. CRITICAL - security
   📄 test-file.js (lines 3-3)
   💬 Potential SQL injection vulnerability
   💡 Suggestion: Use parameterized queries

2. MAJOR - security
   📄 test-file.js (lines 6-6)
   💬 Hardcoded password detected
   💡 Suggestion: Use environment variables

3. MINOR - performance
   📄 test-file.js (lines 9-15)
   💬 Nested loop with O(n²) complexity
   💡 Suggestion: Use Set for duplicate detection
```

### **GitHub PR Comment:**
The bot will automatically comment on your PR with the review results in a nice formatted table.

### **GitHub Status Check:**
- ✅ **Success**: No critical issues found
- ❌ **Failure**: Critical or major issues found
- ⚠️ **Warning**: Minor issues found

---

## 🔧 **Customizing the GitHub Action**

### **Edit the Workflow File**
You can modify `.github/workflows/ai-code-review.yml`:

```yaml
# Change when it runs
on:
  push:
    branches: [ main, develop, staging ]  # Add more branches
  pull_request:
    branches: [ main ]

# Change the failure threshold
--fail-on major  # Fail on major+ issues
--fail-on critical  # Only fail on critical issues

# Add more languages
--language typescript
--project-type react
```

### **Test Different Project Types**
```yaml
# For React projects
--project-type react

# For Next.js projects
--project-type nextjs

# For Node.js APIs
--project-type nodejs

# For Python projects
--project-type python
```

---

## 🛠 **Troubleshooting GitHub Actions**

### **Issue: "No AI providers available"**
- **Solution**: Make sure `OPENROUTER_API_KEY` is set as repository secret

### **Issue: "ai-code-reviewer command not found"**
- **Solution**: The action installs it automatically via pip

### **Issue: "No changes to review"**
- **Solution**: Make sure you have actual code changes in your commits

### **Issue: Action doesn't trigger**
- **Solution**: Make sure the workflow file is in `.github/workflows/` and you pushed to the correct branch

---

## 🎯 **Quick Test Script**

Create this script to test locally before pushing:

```bash
#!/bin/bash
# test-github-action.sh

echo "🧪 Testing AI Code Review Setup"

# Check if workflow file exists
if [ -f ".github/workflows/ai-code-review.yml" ]; then
    echo "✅ GitHub workflow file found"
else
    echo "❌ Missing workflow file - copy it from the main project"
    exit 1
fi

# Test API key (you'll need to set this)
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️ OPENROUTER_API_KEY not set locally (that's OK, GitHub will use the secret)"
else
    echo "✅ API key is set"
fi

# Check git status
if git status | grep -q "nothing to commit"; then
    echo "⚠️ No changes to commit - create some test changes first"
else
    echo "✅ Changes ready to commit"
fi

echo ""
echo "🚀 Ready to push and test!"
echo "Run: git push origin your-branch-name"
```

---

## 🎯 **Expected Timeline**

1. **Push code** → GitHub Action starts (30 seconds)
2. **Setup** → Install dependencies (1-2 minutes)
3. **AI Review** → Analyze your code (1-3 minutes)
4. **Results** → Comments appear on PR (30 seconds)

**Total time: 3-6 minutes** ⏰

---

## 🎉 **Success Indicators**

✅ **GitHub Action completes successfully**
✅ **PR gets AI review comments**
✅ **Status check shows pass/fail**
✅ **Review artifacts uploaded**

You'll know it's working when you see the AI bot commenting on your PR with detailed code review feedback! 🤖