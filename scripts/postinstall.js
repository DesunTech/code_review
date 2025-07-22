#!/usr/bin/env node

const { spawn } = require('cross-spawn');
const fs = require('fs');
const path = require('path');

/**
 * Post-install script for ai-code-reviewer npm package
 * Ensures Python dependencies are available
 */

console.log('🚀 Setting up AI Code Reviewer...');

async function checkPython() {
  try {
    const result = spawn.sync('python3', ['--version'], {
      stdio: 'pipe',
    });
    if (result.status === 0) {
      const version = result.stdout.toString().trim();
      console.log(`✅ Found ${version}`);
      return 'python3';
    }
  } catch (error) {
    // Try python command
    try {
      const result = spawn.sync('python', ['--version'], {
        stdio: 'pipe',
      });
      if (result.status === 0) {
        const version = result.stdout.toString().trim();
        console.log(`✅ Found ${version}`);
        return 'python';
      }
    } catch (error) {
      return null;
    }
  }
  return null;
}

async function checkPip() {
  try {
    const result = spawn.sync('pip', ['--version'], {
      stdio: 'pipe',
    });
    if (result.status === 0) {
      console.log('✅ pip is available');
      return true;
    }
  } catch (error) {
    return false;
  }
  return false;
}

function createSetupInstructions() {
  const instructions = `
# AI Code Reviewer Setup Instructions

## Quick Start for Node.js/React/Next.js Projects

### 1. Install and Use
\`\`\`bash
# Use directly with npx (recommended)
npx ai-code-reviewer --base main --head HEAD

# Or install globally
npm install -g ai-code-reviewer
ai-code-reviewer --list-providers
\`\`\`

### 2. Set up AI Provider (choose one)
\`\`\`bash
# Option 1: Claude (Recommended for quality)
export ANTHROPIC_API_KEY="your-anthropic-key"

# Option 2: OpenAI (Fast and reliable)
export OPENAI_API_KEY="your-openai-key"

# Option 3: OpenRouter (Cost-effective)
export OPENROUTER_API_KEY="your-openrouter-key"

# Option 4: Local models (Free & Private)
# Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh
# ollama pull codellama
\`\`\`

### 3. Project-Specific Usage

#### React Projects
\`\`\`bash
npx ai-code-reviewer --provider auto --language typescript --project-type react
\`\`\`

#### Next.js Projects
\`\`\`bash
npx ai-code-reviewer --provider auto --language typescript --project-type nextjs
\`\`\`

#### React Native Projects
\`\`\`bash
npx ai-code-reviewer --provider auto --language typescript --project-type react-native
\`\`\`

#### Node.js Projects
\`\`\`bash
npx ai-code-reviewer --provider auto --language javascript --project-type nodejs
\`\`\`

### 4. CI/CD Integration
Add to your GitHub Actions workflow:
\`\`\`yaml
- name: AI Code Review
  run: npx ai-code-reviewer --base main --head HEAD --fail-on major
  env:
    ANTHROPIC_API_KEY: \${{ secrets.ANTHROPIC_API_KEY }}
\`\`\`

## Troubleshooting

If you see Python-related errors:
1. Install Python 3.8+: https://www.python.org/downloads/
2. The tool will auto-install Python dependencies on first run

For more help: https://github.com/your-username/ai-code-reviewer
`;

  fs.writeFileSync(
    path.join(process.cwd(), 'AI_CODE_REVIEWER_SETUP.md'),
    instructions
  );
  console.log(
    '📖 Created setup instructions: AI_CODE_REVIEWER_SETUP.md'
  );
}

async function main() {
  const pythonCmd = await checkPython();
  const hasPip = await checkPip();

  if (!pythonCmd) {
    console.log(
      '⚠️  Python not found. The tool will work but requires Python 3.8+'
    );
    console.log('   Install from: https://www.python.org/downloads/');
  }

  if (!hasPip) {
    console.log('⚠️  pip not found. May need manual Python setup.');
  }

  createSetupInstructions();

  console.log('');
  console.log('🎉 AI Code Reviewer is ready!');
  console.log('');
  console.log('Quick start:');
  console.log('  npx ai-code-reviewer --list-providers');
  console.log('  npx ai-code-reviewer --base main --head HEAD');
  console.log('');
  console.log('Set up an AI provider:');
  console.log('  export ANTHROPIC_API_KEY="your-key"  # Recommended');
  console.log('  export OPENAI_API_KEY="your-key"     # Alternative');
  console.log('');
}

main().catch(console.error);
