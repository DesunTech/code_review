# 🚀 Simple Testing Guide for OpenRouter

## ✅ **The Tool is Already Installed!**
When we ran `pip install -e .`, the `ai-code-reviewer` command became available **globally** in your Python environment. You don't need to copy any files!

---

## 🎯 **Simple 3-Step Test Process**

### **Step 1: Set Your API Key (One Time Setup)**
```bash
# Replace with your actual OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-your-actual-key-here"
```

### **Step 2: Test That It Works**
```bash
# This works from ANY directory now
ai-code-reviewer --list-providers
```
**Expected output:**
```
🔍 Available providers: openrouter
```

### **Step 3: Use It On Your Separate Codebase**
```bash
# Go to your other project
cd /path/to/your/react-project  # or wherever your code is

# Run the review (no files needed to copy!)
ai-code-reviewer --provider openrouter --base main --head HEAD
```

---

## 🤔 **Wait, Do I Need to Activate Virtual Environment Every Time?**

**Option A: Use the virtual environment (recommended for this test)**
```bash
# Each time you want to use it
source /Users/desuntechnology/Desktop/tools/code_review/venv/bin/activate
ai-code-reviewer --provider openrouter --base main --head HEAD
```

**Option B: Install globally (easier for daily use)**
```bash
# Install it globally on your system (one time)
pip install -e /Users/desuntechnology/Desktop/tools/code_review

# Then use from anywhere without activation
ai-code-reviewer --provider openrouter --base main --head HEAD
```

---

## 📁 **What Files Go Where?**

### **Your AI Code Review Tool (this directory):**
```
/Users/desuntechnology/Desktop/tools/code_review/
├── ai_code_reviewer/           ← Tool source code
├── venv/                       ← Virtual environment
├── setup.py                    ← Installation config
└── requirements.txt            ← Dependencies
```

### **Your Separate Project (example):**
```
/path/to/your/react-project/
├── src/                        ← Your React code
├── package.json               ← Your project files
├── .git/                      ← Git repository
└── (NO ai-code-reviewer files needed here!)
```

---

## 🧪 **Quick Test Right Now**

Let's test it step by step:

### **Test 1: Check if the command works**
```bash
# From the current directory
source venv/bin/activate
ai-code-reviewer --help
```

### **Test 2: Set your API key and check providers**
```bash
export OPENROUTER_API_KEY="your-actual-key"
ai-code-reviewer --list-providers
```

### **Test 3: Test on this codebase first**
```bash
# Review recent changes in this project
ai-code-reviewer --provider openrouter --base HEAD~1 --head HEAD
```

### **Test 4: Go to your other project**
```bash
# Navigate to your separate codebase
cd /path/to/your/other/project

# The tool still works! No files to copy!
ai-code-reviewer --provider openrouter --base main --head HEAD
```

---

## 🎯 **Real Example**

Let's say your separate project is at `/Users/desuntechnology/Documents/my-react-app`:

```bash
# 1. Set API key (one time)
export OPENROUTER_API_KEY="sk-or-v1-your-key"

# 2. Go to your project
cd /Users/desuntechnology/Documents/my-react-app

# 3. Review your code (tool works from here!)
source /Users/desuntechnology/Desktop/tools/code_review/venv/bin/activate
ai-code-reviewer --provider openrouter --base main --head HEAD
```

**That's it!** No copying, no setup in the other project. The tool is installed and works everywhere! 🚀

---

## ❓ **Still Confused?**

The key insight: `pip install -e .` made `ai-code-reviewer` a **command** available anywhere, just like `git` or `npm`. You don't copy `git` to every project - same here!

```bash
# These all work from anywhere after installation:
git status          ← Git command
npm install         ← NPM command
ai-code-reviewer    ← Your AI tool command
```