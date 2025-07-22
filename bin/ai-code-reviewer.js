#!/usr/bin/env node

const { spawn } = require('cross-spawn');
const which = require('which');
const path = require('path');
const fs = require('fs');

/**
 * AI Code Reviewer - Node.js Wrapper
 *
 * This wrapper allows Node.js/React/Next.js developers to use
 * ai-code-reviewer without installing Python dependencies manually.
 */

async function checkPython() {
  try {
    const pythonCmd = await which('python3').catch(() =>
      which('python')
    );
    return pythonCmd;
  } catch (error) {
    console.error(
      '❌ Python not found. Please install Python 3.8+ first.'
    );
    console.error('   Visit: https://www.python.org/downloads/');
    process.exit(1);
  }
}

async function checkPipInstall() {
  try {
    const result = spawn.sync('pip', ['show', 'ai-code-reviewer'], {
      stdio: 'pipe',
    });
    return result.status === 0;
  } catch (error) {
    return false;
  }
}

async function installAICodeReviewer() {
  console.log('🔄 Installing AI Code Reviewer...');

  const installResult = spawn.sync(
    'pip',
    ['install', 'ai-code-reviewer'],
    {
      stdio: 'inherit',
    }
  );

  if (installResult.status !== 0) {
    console.error('❌ Failed to install ai-code-reviewer via pip');
    console.error('   Try: pip install ai-code-reviewer');
    process.exit(1);
  }

  console.log('✅ AI Code Reviewer installed successfully!');
}

function detectProjectInfo() {
  const cwd = process.cwd();
  let language = 'javascript';
  let projectType = 'general';

  // Detect project type from package.json
  const packageJsonPath = path.join(cwd, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    try {
      const packageJson = JSON.parse(
        fs.readFileSync(packageJsonPath, 'utf8')
      );
      const deps = {
        ...packageJson.dependencies,
        ...packageJson.devDependencies,
      };

      if (deps['react-native']) {
        projectType = 'react-native';
        language = 'typescript';
      } else if (deps['next']) {
        projectType = 'nextjs';
        language = 'typescript';
      } else if (deps['react']) {
        projectType = 'react';
        language = 'typescript';
      } else if (deps['vue']) {
        projectType = 'vue';
      } else if (deps['angular']) {
        projectType = 'angular';
        language = 'typescript';
      } else {
        projectType = 'nodejs';
      }

      // Check if TypeScript is used
      if (
        deps['typescript'] ||
        fs.existsSync(path.join(cwd, 'tsconfig.json'))
      ) {
        language = 'typescript';
      }
    } catch (error) {
      // Ignore errors, use defaults
    }
  }

  return { language, projectType };
}

async function main() {
  const args = process.argv.slice(2);

  // Show help if no arguments
  if (args.length === 0) {
    console.log(
      '🤖 AI Code Reviewer for Node.js/React/Next.js Projects'
    );
    console.log('');
    console.log('Quick Start:');
    console.log('  npx ai-code-reviewer --base main --head HEAD');
    console.log('  npx ai-code-reviewer --list-providers');
    console.log(
      '  npx ai-code-reviewer --provider claude --output json'
    );
    console.log('');
    console.log('Environment Setup:');
    console.log('  export ANTHROPIC_API_KEY="your-claude-key"');
    console.log('  export OPENAI_API_KEY="your-openai-key"');
    console.log('  export OPENROUTER_API_KEY="your-openrouter-key"');
    console.log('');
    args.push('--help');
  }

  // Check Python installation
  const pythonCmd = await checkPython();

  // Check if ai-code-reviewer is installed
  const isInstalled = await checkPipInstall();
  if (!isInstalled) {
    await installAICodeReviewer();
  }

  // Auto-detect project info if not specified
  const projectInfo = detectProjectInfo();
  const finalArgs = [...args];

  // Add auto-detected language and project type if not specified
  if (!args.includes('--language') && !args.includes('-l')) {
    finalArgs.push('--language', projectInfo.language);
  }
  if (!args.includes('--project-type') && !args.includes('-p')) {
    finalArgs.push('--project-type', projectInfo.projectType);
  }

  console.log(
    `🔍 Detected: ${projectInfo.language} ${projectInfo.projectType} project`
  );

  // Run the AI code reviewer
  const result = spawn('ai-code-reviewer', finalArgs, {
    stdio: 'inherit',
    cwd: process.cwd(),
  });

  result.on('error', (error) => {
    console.error(
      '❌ Error running ai-code-reviewer:',
      error.message
    );
    process.exit(1);
  });

  result.on('exit', (code) => {
    process.exit(code || 0);
  });
}

// Run the wrapper
main().catch((error) => {
  console.error('❌ Unexpected error:', error);
  process.exit(1);
});
