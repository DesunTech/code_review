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
    """AI-powered code review system using Claude API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-opus-20240229"
        self.reviews: List[CodeReview] = []
        
    async def review_diff(self, diff_content: str, context: Dict[str, any] = None) -> List[CodeReview]:
        """Review a git diff and return findings."""
        prompt = self._create_review_prompt(diff_content, context)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": self.model,
                "max_tokens": 4000,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }
            
            async with session.post(self.base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_review_response(result['content'][0]['text'])
                else:
                    raise Exception(f"API request failed: {response.status}")
    
    def _create_review_prompt(self, diff_content: str, context: Dict[str, any] = None) -> str:
        """Create a comprehensive review prompt."""
        language = context.get('language', 'unknown') if context else 'unknown'
        project_type = context.get('project_type', 'general') if context else 'general'
        
        return f"""You are an expert code reviewer. Review the following code diff and provide detailed feedback.

IMPORTANT: Respond ONLY with a valid JSON array of review findings. Each finding should have this exact structure:
[
  {{
    "severity": "critical|major|minor|info",
    "category": "performance|security|style|logic|best-practice",
    "file": "filename",
    "line_start": line_number,
    "line_end": line_number,
    "message": "Clear description of the issue",
    "suggestion": "How to fix it (optional)",
    "code_snippet": "Problematic code (optional)"
  }}
]

Focus on:
1. Performance issues (O(n²) loops, unnecessary computations, memory leaks)
2. Security vulnerabilities (SQL injection, XSS, authentication issues)
3. Logic errors and edge cases
4. Anti-patterns and code smells
5. Best practices for {language} and {project_type} projects
6. Error handling and null checks
7. Resource management (file handles, connections, etc.)
8. Concurrency issues (race conditions, deadlocks)
9. Code maintainability and readability

Here's the diff to review:

```diff
{diff_content}
```

Provide actionable feedback with specific line numbers from the diff. Be thorough but focus on important issues.
Your entire response MUST be a valid JSON array. DO NOT include any text outside the JSON structure."""

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
    parser = argparse.ArgumentParser(description="AI-powered code review tool")
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
    
    args = parser.parse_args()
    
    # Initialize components
    reviewer = AICodeReviewer()
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