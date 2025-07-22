import os
import subprocess
import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp
from pathlib import Path

# Import the multi-provider system
from multi_provider_integration import MultiProviderReviewer, ProviderConfig

@dataclass
class CodeReview:
    """Represents a code review with findings and suggestions."""
    severity: str  # 'critical', 'major', 'minor', 'info'
    category: str  # 'performance', 'security', 'style', 'logic', 'best-practice'
    file: str
    line_start: int
    line_end: int
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None

class AICodeReviewer:
    """AI-powered code review system with multi-provider support."""

    def __init__(self, primary_provider: str = None, fallback_providers: List[str] = None):
        # Auto-detect available providers based on API keys
        self.available_providers = self._detect_available_providers()
        print(f"🔍 Available providers: {', '.join(self.available_providers)}")

        # Set primary provider (auto-select if not specified)
        if primary_provider and primary_provider in self.available_providers:
            self.primary_provider = primary_provider
        else:
            self.primary_provider = self._auto_select_primary()

        # Set fallback providers
        if fallback_providers:
            self.fallback_providers = [p for p in fallback_providers if p in self.available_providers]
        else:
            self.fallback_providers = [p for p in self.available_providers if p != self.primary_provider]

        print(f"🎯 Primary provider: {self.primary_provider}")
        print(f"🔄 Fallback providers: {', '.join(self.fallback_providers)}")

        # Initialize the multi-provider reviewer
        self.reviewer = MultiProviderReviewer(
            primary_provider=self.primary_provider,
            fallback_providers=self.fallback_providers
        )
        self.reviews: List[CodeReview] = []

    def _detect_available_providers(self) -> List[str]:
        """Detect available providers based on API keys and endpoints."""
        providers = []

        # Check for Anthropic/Claude
        if os.getenv('ANTHROPIC_API_KEY'):
            providers.append('claude')

        # Check for OpenAI
        if os.getenv('OPENAI_API_KEY'):
            providers.append('openai')

        # Check for OpenRouter
        if os.getenv('OPENROUTER_API_KEY'):
            providers.append('openrouter')

        # Check for local models (assume available if endpoint is configured)
        local_endpoint = os.getenv('LOCAL_MODEL_ENDPOINT', 'http://localhost:11434/api/generate')
        try:
            # Quick check if local endpoint is reachable
            import requests
            response = requests.get(local_endpoint.replace('/api/generate', '/api/tags'), timeout=2)
            if response.status_code == 200:
                providers.append('local')
        except:
            # Local model not available
            pass

        return providers

    def _auto_select_primary(self) -> str:
        """Auto-select the best available primary provider."""
        # Priority order: claude > openai > openrouter > local
        priority_order = ['claude', 'openai', 'openrouter', 'local']

        for provider in priority_order:
            if provider in self.available_providers:
                return provider

        # If no providers available, raise error
        if not self.available_providers:
            raise Exception("❌ No AI providers available! Please set up at least one API key.")

        return self.available_providers[0]

    async def review_diff(self, diff_content: str, context: Dict[str, any] = None) -> List[CodeReview]:
        """Review a git diff and return findings using multi-provider system."""
        try:
            response_text = await self.reviewer.review_code(diff_content, context)
            return self._parse_review_response(response_text)
        except Exception as e:
            print(f"❌ All providers failed: {e}")
            return []

    def _parse_review_response(self, response_text: str) -> List[CodeReview]:
        """Parse the AI response into CodeReview objects."""
        try:
            # Clean the response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            findings = json.loads(response_text.strip())

            reviews = []
            for finding in findings:
                review = CodeReview(
                    severity=finding['severity'],
                    category=finding['category'],
                    file=finding['file'],
                    line_start=finding['line_start'],
                    line_end=finding['line_end'],
                    message=finding['message'],
                    suggestion=finding.get('suggestion'),
                    code_snippet=finding.get('code_snippet')
                )
                reviews.append(review)

            return reviews
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response: {e}")
            print(f"Response was: {response_text[:500]}...")
            return []

class GitIntegration:
    """Handle Git operations for code review."""

    @staticmethod
    def get_diff(base_branch: str = "main", head_branch: str = "HEAD") -> str:
        """Get the diff between two branches."""
        try:
            result = subprocess.run(
                ["git", "diff", f"{base_branch}...{head_branch}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get git diff: {e}")

    @staticmethod
    def get_changed_files(base_branch: str = "main", head_branch: str = "HEAD") -> List[str]:
        """Get list of changed files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_branch}...{head_branch}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n') if result.stdout else []
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get changed files: {e}")

class CodeQualityEnforcer:
    """Enforce code quality standards based on review findings."""

    def __init__(self, fail_on_severity: str = "major"):
        self.fail_on_severity = fail_on_severity
        self.severity_levels = {
            'critical': 4,
            'major': 3,
            'minor': 2,
            'info': 1
        }

    def should_fail(self, reviews: List[CodeReview]) -> bool:
        """Determine if the code review should fail the build."""
        threshold = self.severity_levels.get(self.fail_on_severity, 3)

        for review in reviews:
            if self.severity_levels.get(review.severity, 0) >= threshold:
                return True
        return False

    def generate_report(self, reviews: List[CodeReview], output_format: str = "markdown") -> str:
        """Generate a formatted report of the findings."""
        if output_format == "markdown":
            return self._generate_markdown_report(reviews)
        elif output_format == "json":
            return json.dumps([vars(r) for r in reviews], indent=2)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _generate_markdown_report(self, reviews: List[CodeReview]) -> str:
        """Generate a markdown report."""
        if not reviews:
            return "# Code Review Report\n\n✅ No issues found!"

        report = ["# Code Review Report", f"\nGenerated at: {datetime.now().isoformat()}",
                  f"\nTotal findings: {len(reviews)}\n"]

        # Summary by severity
        severity_counts = {}
        for review in reviews:
            severity_counts[review.severity] = severity_counts.get(review.severity, 0) + 1

        report.append("## Summary")
        for severity in ['critical', 'major', 'minor', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {'critical': '🔴', 'major': '🟠', 'minor': '🟡', 'info': 'ℹ️'}[severity]
                report.append(f"- {emoji} {severity.capitalize()}: {count}")

        # Detailed findings
        report.append("\n## Detailed Findings\n")

        for i, review in enumerate(reviews, 1):
            emoji = {'critical': '🔴', 'major': '🟠', 'minor': '🟡', 'info': 'ℹ️'}[review.severity]

            report.append(f"### {i}. {emoji} [{review.severity.upper()}] {review.category}")
            report.append(f"**File:** `{review.file}` (Lines {review.line_start}-{review.line_end})")
            report.append(f"\n{review.message}")

            if review.code_snippet:
                report.append(f"\n**Code:**\n```\n{review.code_snippet}\n```")

            if review.suggestion:
                report.append(f"\n**Suggestion:** {review.suggestion}")

            report.append("")

        return "\n".join(report)

async def main():
    """Main entry point for the code review tool."""
    parser = argparse.ArgumentParser(description="AI-powered code review tool with multi-provider support")
    parser.add_argument("--base", default="main", help="Base branch for comparison")
    parser.add_argument("--head", default="HEAD", help="Head branch for comparison")
    parser.add_argument("--output", default="markdown", choices=["markdown", "json"],
                       help="Output format")
    parser.add_argument("--fail-on", default="major",
                       choices=["critical", "major", "minor", "info"],
                       help="Fail threshold for CI/CD")
    parser.add_argument("--save-report", help="Save report to file")
    parser.add_argument("--language", help="Primary language of the project")
    parser.add_argument("--project-type", help="Type of project (web, api, cli, etc.)")

    # New provider selection arguments
    parser.add_argument("--provider",
                       choices=["claude", "openai", "openrouter", "local", "auto"],
                       default="auto",
                       help="Primary AI provider to use (auto-detects if not specified)")
    parser.add_argument("--fallback-providers",
                       nargs="*",
                       choices=["claude", "openai", "openrouter", "local"],
                       help="Fallback providers to use if primary fails")
    parser.add_argument("--list-providers",
                       action="store_true",
                       help="List available providers and exit")

    args = parser.parse_args()

    # Handle list providers option
    if args.list_providers:
        print("🔍 Detecting available AI providers...")
        temp_reviewer = AICodeReviewer()
        if temp_reviewer.available_providers:
            print("\n✅ Available providers:")
            for provider in temp_reviewer.available_providers:
                print(f"  - {provider}")
        else:
            print("\n❌ No providers available. Please set up API keys.")
        return 0

    # Initialize components with provider selection
    primary_provider = None if args.provider == "auto" else args.provider
    try:
        reviewer = AICodeReviewer(
            primary_provider=primary_provider,
            fallback_providers=args.fallback_providers
        )
    except Exception as e:
        print(f"❌ Failed to initialize AI reviewer: {e}")
        print("\n💡 Available setup options:")
        print("  - Set ANTHROPIC_API_KEY for Claude")
        print("  - Set OPENAI_API_KEY for OpenAI")
        print("  - Set OPENROUTER_API_KEY for OpenRouter")
        print("  - Set up Ollama locally for local models")
        return 1

    git = GitIntegration()
    enforcer = CodeQualityEnforcer(fail_on_severity=args.fail_on)

    # Get the diff
    print("📝 Getting code changes...")
    try:
        diff_content = git.get_diff(args.base, args.head)
        if not diff_content:
            print("✅ No changes to review!")
            return 0
    except Exception as e:
        print(f"❌ Error getting diff: {e}")
        return 1

    # Perform the review
    print("🤖 Analyzing code...")
    context = {
        'language': args.language,
        'project_type': args.project_type
    }

    try:
        reviews = await reviewer.review_diff(diff_content, context)
    except Exception as e:
        print(f"❌ Error during review: {e}")
        return 1

    # Generate report
    report = enforcer.generate_report(reviews, args.output)
    print("\n" + report)

    # Save report if requested
    if args.save_report:
        with open(args.save_report, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.save_report}")

    # Determine exit code
    if enforcer.should_fail(reviews):
        print(f"\n❌ Code review failed! Found issues at or above '{args.fail_on}' severity.")
        return 1
    else:
        print(f"\n✅ Code review passed!")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

def cli_main():
    """Entry point for console script."""
    exit_code = asyncio.run(main())
    exit(exit_code)