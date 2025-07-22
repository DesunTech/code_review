# AI Code Reviewer

An AI-powered code review system that analyzes git diffs using multiple AI providers (Claude, OpenAI, etc.) to detect performance, security, style, logic, and best practice issues. Generates reports and integrates with CI/CD pipelines like GitHub Actions.

## Features
- AI-driven code analysis with multi-provider support
- Git integration for diff fetching
- Configurable severity thresholds and custom rules
- Reports in Markdown/JSON
- CI/CD integrations (GitHub Actions, GitLab, Jenkins, pre-commit)
- Benchmarking for AI providers
- Extensible with custom analyzers and prompts

## How to Use
1. Install: See [setup-guide.md](setup-guide.md) for installation and virtual env setup.
2. Run locally: `python ai-code-reviewer.py --base main --head HEAD`
3. Configure: Edit `.ai-code-review.yml` or use env vars (see setup-guide.md).
4. As GitHub Action: Copy workflow to `.github/workflows/` and set secrets (details in setup-guide.md).

For detailed usage, configuration, and integrations, refer to [setup-guide.md](setup-guide.md).

## Project Structure
- `ai-code-reviewer.py`: Core reviewer script
- `multi-provider-integration.py`: Multi-AI provider support and benchmarking
- `config_manager.py`: Configuration loading and validation
- `code-review-config.txt`: Sample configuration
- `github-actions-workflow.txt`: GitHub Actions workflow template
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