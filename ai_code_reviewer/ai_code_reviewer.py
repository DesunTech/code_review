import os
import subprocess
import json
import argparse
import re
from typing import List, Dict, Optional, NamedTuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp
from pathlib import Path

# Import the multi-provider system
from .multi_provider_integration import MultiProviderReviewer, ProviderConfig

class DiffHunk(NamedTuple):
    """Represents a single diff hunk with context."""
    file_path: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[str]
    context_before: List[str]
    context_after: List[str]

class FileContext(NamedTuple):
    """Represents file context with imports and metadata."""
    file_path: str
    language: str
    imports: List[str]
    functions: List[str]
    classes: List[str]
    total_lines: int

class DependencyMap(NamedTuple):
    """Represents cross-file dependencies."""
    changed_exports: Dict[str, List[str]]  # file -> exported functions/classes
    affected_files: Dict[str, List[str]]   # file -> files that import it
    breaking_changes: List[str]            # potential breaking changes
    related_files: List[str]               # files to consider for context

class ArchitecturePattern(NamedTuple):
    """Represents detected architecture patterns."""
    pattern_type: str                      # MVC, MVP, Clean Architecture, etc.
    confidence: float                      # 0.0 to 1.0
    evidence: List[str]                    # files/patterns that indicate this architecture
    description: str                       # human-readable description

class ArchitectureAnalysis(NamedTuple):
    """Comprehensive architecture analysis."""
    detected_patterns: List[ArchitecturePattern]
    project_structure: Dict[str, List[str]]  # layer -> files
    design_issues: List[str]                 # architectural problems
    recommendations: List[str]               # improvement suggestions
    complexity_metrics: Dict[str, float]     # various complexity measurements
    tech_stack: Dict[str, List[str]]         # technology categories -> technologies

@dataclass
class CodeReview:
    """Represents a code review with findings, suggestions, and fixes."""
    severity: str  # 'critical', 'major', 'minor', 'info'
    category: str  # 'performance', 'security', 'style', 'logic', 'best-practice'
    file: str
    line_start: int
    line_end: int
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    # Enhanced fields for better fixes
    fixed_code: Optional[str] = None  # The corrected code snippet
    impact: Optional[str] = None      # Potential impact if not fixed
    confidence: Optional[str] = None  # AI confidence level (high/medium/low)

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
        self.architecture_analysis: ArchitectureAnalysis = None

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
        """Review a git diff and return findings using multi-provider system with enhanced context."""
        try:
            # Parse diff into structured hunks with context
            print("🔍 Parsing diff and extracting context...")
            hunks = GitIntegration.parse_diff_hunks(diff_content)
            
            # Gather file contexts for changed files
            file_contexts = {}
            changed_files = set(hunk.file_path for hunk in hunks)
            
            for file_path in list(changed_files)[:5]:  # Limit to avoid overwhelming context
                file_contexts[file_path] = GitIntegration.get_file_context(file_path)
            
            # Analyze cross-file dependencies
            dependency_map = GitIntegration.analyze_cross_file_dependencies(
                list(changed_files), hunks
            )
            
            # Perform architecture analysis
            architecture_analysis = GitIntegration.analyze_project_architecture(list(changed_files))
            
            # Store architecture analysis for report generation
            self.architecture_analysis = architecture_analysis
            
            # Enhance context with structured information
            enhanced_context = context.copy() if context else {}
            enhanced_context.update({
                'hunks': hunks,
                'file_contexts': file_contexts,
                'dependency_map': dependency_map,
                'architecture_analysis': architecture_analysis,
                'changed_files_count': len(changed_files),
                'total_hunks': len(hunks),
                'breaking_changes_count': len(dependency_map.breaking_changes),
                'affected_files_count': len([f for files in dependency_map.affected_files.values() for f in files]),
                'architecture_patterns_count': len(architecture_analysis.detected_patterns),
                'design_issues_count': len(architecture_analysis.design_issues)
            })
            
            print(f"📊 Context gathered: {len(changed_files)} files, {len(hunks)} hunks, {len(dependency_map.breaking_changes)} breaking changes")
            print(f"🏗️ Architecture: {len(architecture_analysis.detected_patterns)} patterns, {len(architecture_analysis.design_issues)} issues, {len(architecture_analysis.recommendations)} recommendations")
            
            response_text = await self.reviewer.review_code(diff_content, enhanced_context)
            return self._parse_review_response(response_text)
        except Exception as e:
            print(f"❌ All providers failed: {e}")
            return []

    def _parse_review_response(self, response_text: str) -> List[CodeReview]:
        """Parse the AI response into CodeReview objects with robust error handling."""
        try:
            # Clean the response text more aggressively
            response_text = response_text.strip()
            
            # Remove common markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            # Remove any leading/trailing text before/after JSON
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx + 1]
            
            # Additional cleaning for common issues
            response_text = response_text.replace('\n', ' ').replace('\r', ' ')
            # Fix common JSON formatting issues
            response_text = response_text.replace('",}', '"}').replace(',]', ']')

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
                    code_snippet=finding.get('code_snippet'),
                    # Enhanced fields
                    fixed_code=finding.get('fixed_code'),
                    impact=finding.get('impact'),
                    confidence=finding.get('confidence')
                )
                reviews.append(review)

            return reviews
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response: {e}")
            print(f"📝 Raw response preview: {response_text[:200]}...")
            
            # Try to extract any useful information as a fallback
            fallback_reviews = self._create_fallback_review(response_text)
            if fallback_reviews:
                print("🔄 Using fallback parsing...")
                return fallback_reviews
            
            return []
        except Exception as e:
            print(f"❌ Unexpected error parsing response: {e}")
            return []
    
    def _create_fallback_review(self, response_text: str) -> List[CodeReview]:
        """Create a basic review from malformed response."""
        try:
            # If we can't parse JSON, create a simple review noting the parsing failure
            return [CodeReview(
                severity="info",
                category="system",
                file="unknown",
                line_start=1,
                line_end=1,
                message="AI model returned malformed response - please try again or switch models",
                suggestion="Consider using a different AI model or reducing diff complexity",
                code_snippet="",
                fixed_code="",
                impact="Unable to analyze code due to parsing issues",
                confidence="low"
            )]
        except:
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

    @staticmethod
    def get_file_content(file_path: str, ref: str = "HEAD") -> str:
        """Get content of a file at a specific git reference."""
        try:
            result = subprocess.run(
                ["git", "show", f"{ref}:{file_path}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            # File might be new or deleted, try to read from working directory
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                return ""

    @staticmethod
    def parse_diff_hunks(diff_content: str) -> List[DiffHunk]:
        """Parse git diff into structured hunks with context."""
        hunks = []
        current_file = None
        current_hunk = None
        hunk_lines = []
        
        for line in diff_content.split('\n'):
            # New file header
            if line.startswith('diff --git'):
                if current_hunk and current_file:
                    hunks.append(GitIntegration._create_hunk_with_context(
                        current_file, current_hunk, hunk_lines
                    ))
                current_file = None
                current_hunk = None
                hunk_lines = []
                
                # Extract file path from diff header
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
            
            # Hunk header (@@)
            elif line.startswith('@@') and current_file:
                if current_hunk:
                    hunks.append(GitIntegration._create_hunk_with_context(
                        current_file, current_hunk, hunk_lines
                    ))
                
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                match = re.search(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2) or 1)
                    new_start = int(match.group(3))
                    new_count = int(match.group(4) or 1)
                    
                    current_hunk = (old_start, old_count, new_start, new_count)
                    hunk_lines = []
            
            # Hunk content
            elif current_hunk and current_file:
                if line.startswith((' ', '+', '-')):
                    hunk_lines.append(line)
        
        # Handle last hunk
        if current_hunk and current_file:
            hunks.append(GitIntegration._create_hunk_with_context(
                current_file, current_hunk, hunk_lines
            ))
        
        return hunks

    @staticmethod
    def _create_hunk_with_context(file_path: str, hunk_info: tuple, hunk_lines: List[str]) -> DiffHunk:
        """Create a DiffHunk with surrounding context."""
        old_start, old_count, new_start, new_count = hunk_info
        
        # Get surrounding context (±10 lines)
        context_before = GitIntegration._get_context_lines(file_path, max(1, new_start - 10), new_start - 1)
        context_after = GitIntegration._get_context_lines(file_path, new_start + new_count, new_start + new_count + 10)
        
        return DiffHunk(
            file_path=file_path,
            old_start=old_start,
            old_count=old_count,
            new_start=new_start,
            new_count=new_count,
            lines=hunk_lines,
            context_before=context_before,
            context_after=context_after
        )

    @staticmethod
    def _get_context_lines(file_path: str, start_line: int, end_line: int) -> List[str]:
        """Get specific lines from a file for context."""
        try:
            file_content = GitIntegration.get_file_content(file_path)
            lines = file_content.split('\n')
            
            # Adjust for 0-based indexing
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            
            return lines[start_idx:end_idx]
        except Exception:
            return []

    @staticmethod
    def get_file_context(file_path: str) -> FileContext:
        """Extract file context including imports, functions, and classes."""
        try:
            content = GitIntegration.get_file_content(file_path)
            lines = content.split('\n')
            
            language = GitIntegration._detect_language(file_path)
            imports = GitIntegration._extract_imports(content, language)
            functions = GitIntegration._extract_functions(content, language)
            classes = GitIntegration._extract_classes(content, language)
            
            return FileContext(
                file_path=file_path,
                language=language,
                imports=imports,
                functions=functions,
                classes=classes,
                total_lines=len(lines)
            )
        except Exception:
            return FileContext(file_path, "unknown", [], [], [], 0)

    @staticmethod
    def _detect_language(file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sql': 'sql'
        }
        return language_map.get(ext, 'unknown')

    @staticmethod
    def _extract_imports(content: str, language: str) -> List[str]:
        """Extract import statements based on language."""
        imports = []
        
        if language == 'python':
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith(('import ', 'from ')):
                    imports.append(line)
        elif language in ['javascript', 'typescript']:
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith(('import ', 'const ', 'require(')):
                    if 'import' in line or 'require' in line:
                        imports.append(line)
        elif language == 'java':
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import '):
                    imports.append(line)
        elif language == 'go':
            in_import_block = False
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ('):
                    in_import_block = True
                    continue
                elif line == ')' and in_import_block:
                    in_import_block = False
                    continue
                elif in_import_block or line.startswith('import '):
                    imports.append(line)
        
        return imports[:10]  # Limit to avoid overwhelming context

    @staticmethod
    def _extract_functions(content: str, language: str) -> List[str]:
        """Extract function names based on language."""
        functions = []
        
        if language == 'python':
            pattern = r'^\s*def\s+(\w+)\s*\('
            functions = re.findall(pattern, content, re.MULTILINE)
        elif language in ['javascript', 'typescript']:
            patterns = [
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*\(',
                r'(\w+)\s*:\s*\([^)]*\)\s*=>'
            ]
            for pattern in patterns:
                functions.extend(re.findall(pattern, content))
        elif language == 'java':
            pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\('
            matches = re.findall(pattern, content)
            functions = [match[2] for match in matches if match[2]]
        elif language == 'go':
            pattern = r'func\s+(\w+)\s*\('
            functions = re.findall(pattern, content)
        
        return functions[:15]  # Limit to avoid overwhelming context

    @staticmethod
    def _extract_classes(content: str, language: str) -> List[str]:
        """Extract class names based on language."""
        classes = []
        
        if language == 'python':
            pattern = r'^\s*class\s+(\w+).*:'
            classes = re.findall(pattern, content, re.MULTILINE)
        elif language in ['javascript', 'typescript']:
            patterns = [
                r'class\s+(\w+)',
                r'interface\s+(\w+)',
                r'type\s+(\w+)\s*='
            ]
            for pattern in patterns:
                classes.extend(re.findall(pattern, content))
        elif language == 'java':
            patterns = [
                r'(public|private)?\s*class\s+(\w+)',
                r'(public|private)?\s*interface\s+(\w+)'
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                classes.extend([match[1] for match in matches if match[1]])
        elif language == 'go':
            pattern = r'type\s+(\w+)\s+struct'
            classes = re.findall(pattern, content)
        
        return classes[:10]  # Limit to avoid overwhelming context

    @staticmethod
    def analyze_cross_file_dependencies(changed_files: List[str], hunks: List[DiffHunk]) -> DependencyMap:
        """Analyze cross-file dependencies and potential breaking changes."""
        print("🔗 Analyzing cross-file dependencies...")
        
        changed_exports = {}
        affected_files = {}
        breaking_changes = []
        related_files = set()
        
        # Analyze exports from changed files
        for file_path in changed_files:
            file_context = GitIntegration.get_file_context(file_path)
            exports = GitIntegration._extract_exports(file_path, file_context.language)
            if exports:
                changed_exports[file_path] = exports
        
        # Find files that might be affected by changes
        for changed_file in changed_files:
            affecting = GitIntegration._find_files_importing(changed_file)
            if affecting:
                affected_files[changed_file] = affecting
                related_files.update(affecting)
        
        # Detect potential breaking changes
        for hunk in hunks:
            breaking = GitIntegration._detect_breaking_changes(hunk)
            breaking_changes.extend(breaking)
        
        # Add related files from imports
        for file_path in changed_files:
            imports = GitIntegration._extract_imported_files(file_path)
            related_files.update(imports[:10])  # Limit to avoid overwhelming
        
        print(f"📊 Dependencies: {len(changed_exports)} files with exports, {len(affected_files)} with dependents")
        
        return DependencyMap(
            changed_exports=changed_exports,
            affected_files=affected_files,
            breaking_changes=breaking_changes,
            related_files=list(related_files)[:20]  # Limit to most relevant
        )

    @staticmethod
    def _extract_exports(file_path: str, language: str) -> List[str]:
        """Extract exported functions, classes, and variables."""
        try:
            content = GitIntegration.get_file_content(file_path)
            exports = []
            
            if language == 'python':
                # Look for functions and classes (assuming public if no leading underscore)
                functions = re.findall(r'^\s*def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(', content, re.MULTILINE)
                classes = re.findall(r'^\s*class\s+([a-zA-Z][a-zA-Z0-9_]*)', content, re.MULTILINE)
                # Look for __all__ exports
                all_match = re.search(r'__all__\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if all_match:
                    all_exports = re.findall(r'["\']([^"\']+)["\']', all_match.group(1))
                    exports.extend(all_exports)
                else:
                    # Public functions and classes
                    exports.extend([f for f in functions if not f.startswith('_')])
                    exports.extend([c for c in classes if not c.startswith('_')])
                    
            elif language in ['javascript', 'typescript']:
                # Named exports
                named_exports = re.findall(r'export\s+(?:const|let|var|function|class)\s+(\w+)', content)
                exports.extend(named_exports)
                
                # Export statements
                export_statements = re.findall(r'export\s*\{\s*([^}]+)\s*\}', content)
                for statement in export_statements:
                    names = re.findall(r'(\w+)', statement)
                    exports.extend(names)
                
                # Default exports (use filename)
                if re.search(r'export\s+default', content):
                    from pathlib import Path
                    default_name = Path(file_path).stem
                    exports.append(f"default:{default_name}")
                    
            elif language == 'java':
                # Public classes and methods
                public_classes = re.findall(r'public\s+class\s+(\w+)', content)
                public_methods = re.findall(r'public\s+(?:static\s+)?\w+\s+(\w+)\s*\(', content)
                exports.extend(public_classes)
                exports.extend(public_methods)
                
            elif language == 'go':
                # Exported functions and types (start with capital letter)
                functions = re.findall(r'func\s+([A-Z][a-zA-Z0-9_]*)', content)
                types = re.findall(r'type\s+([A-Z][a-zA-Z0-9_]*)', content)
                exports.extend(functions)
                exports.extend(types)
            
            return list(set(exports))[:15]  # Remove duplicates and limit
            
        except Exception:
            return []

    @staticmethod
    def _find_files_importing(target_file: str) -> List[str]:
        """Find files that import the target file."""
        try:
            # Use git grep to find imports
            file_stem = Path(target_file).stem
            file_name = Path(target_file).name
            
            patterns_to_search = [
                f'import.*{file_stem}',
                f'from.*{file_stem}',
                f'require.*{file_name}',
                f'import.*{file_name}'
            ]
            
            importing_files = set()
            
            for pattern in patterns_to_search:
                try:
                    result = subprocess.run(
                        ["git", "grep", "-l", pattern],
                        capture_output=True,
                        text=True,
                        cwd="."
                    )
                    if result.returncode == 0:
                        files = result.stdout.strip().split('\n')
                        importing_files.update([f for f in files if f and f != target_file])
                except subprocess.CalledProcessError:
                    continue
            
            return list(importing_files)[:10]  # Limit to avoid overwhelming
            
        except Exception:
            return []

    @staticmethod
    def _detect_breaking_changes(hunk: DiffHunk) -> List[str]:
        """Detect potential breaking changes in a diff hunk."""
        breaking_changes = []
        
        # Look for removed or modified exports
        for line in hunk.lines:
            if line.startswith('-'):
                line_content = line[1:].strip()
                
                # Function/method removal or signature change
                if re.match(r'(def|function|public.*)\s+\w+\s*\(', line_content):
                    breaking_changes.append(f"Function signature change in {hunk.file_path}:{hunk.new_start}")
                
                # Class removal
                if re.match(r'class\s+\w+', line_content):
                    breaking_changes.append(f"Class definition change in {hunk.file_path}:{hunk.new_start}")
                
                # Export removal
                if 'export' in line_content and any(keyword in line_content for keyword in ['function', 'class', 'const', 'let']):
                    breaking_changes.append(f"Export removal in {hunk.file_path}:{hunk.new_start}")
                
                # API endpoint changes
                if any(keyword in line_content.lower() for keyword in ['@app.route', '@router', 'app.get', 'app.post']):
                    breaking_changes.append(f"API endpoint change in {hunk.file_path}:{hunk.new_start}")
        
        return breaking_changes

    @staticmethod
    def _extract_imported_files(file_path: str) -> List[str]:
        """Extract files that this file imports for context."""
        try:
            content = GitIntegration.get_file_content(file_path)
            language = GitIntegration._detect_language(file_path)
            imported_files = []
            
            if language == 'python':
                # Relative imports
                relative_imports = re.findall(r'from\s+\.(\w+)', content)
                for imp in relative_imports:
                    # Try to find the actual file
                    base_dir = Path(file_path).parent
                    possible_files = [
                        base_dir / f"{imp}.py",
                        base_dir / imp / "__init__.py"
                    ]
                    for possible_file in possible_files:
                        if possible_file.exists():
                            imported_files.append(str(possible_file))
                            break
                
                # Local imports (same directory)
                local_imports = re.findall(r'import\s+(\w+)', content)
                local_imports.extend(re.findall(r'from\s+(\w+)\s+import', content))
                base_dir = Path(file_path).parent
                for imp in local_imports:
                    if not imp.startswith(('os', 'sys', 'json', 'typing', 're')):  # Skip stdlib
                        possible_file = base_dir / f"{imp}.py"
                        if possible_file.exists():
                            imported_files.append(str(possible_file))
            
            elif language in ['javascript', 'typescript']:
                # Relative imports
                relative_imports = re.findall(r'import.*from\s+["\'](\./.*?)["\']', content)
                relative_imports.extend(re.findall(r'require\(["\'](\./.*?)["\']\)', content))
                
                base_dir = Path(file_path).parent
                for imp in relative_imports:
                    # Clean up the path
                    imp_path = imp.replace('./', '')
                    possible_files = [
                        base_dir / f"{imp_path}.js",
                        base_dir / f"{imp_path}.ts",
                        base_dir / f"{imp_path}.tsx",
                        base_dir / f"{imp_path}/index.js",
                        base_dir / f"{imp_path}/index.ts"
                    ]
                    for possible_file in possible_files:
                        if possible_file.exists():
                            imported_files.append(str(possible_file))
                            break
            
            return imported_files
            
        except Exception:
            return []

    @staticmethod
    def analyze_project_architecture(changed_files: List[str], all_files: List[str] = None) -> ArchitectureAnalysis:
        """Analyze project architecture patterns and provide recommendations."""
        print("🏗️ Analyzing project architecture...")
        
        if not all_files:
            all_files = GitIntegration._discover_all_project_files()
        
        # Detect architecture patterns
        detected_patterns = GitIntegration._detect_architecture_patterns(all_files)
        
        # Analyze project structure
        project_structure = GitIntegration._analyze_project_structure(all_files)
        
        # Identify design issues
        design_issues = GitIntegration._identify_design_issues(all_files, changed_files)
        
        # Generate recommendations
        recommendations = GitIntegration._generate_architecture_recommendations(
            detected_patterns, project_structure, design_issues, changed_files
        )
        
        # Calculate complexity metrics
        complexity_metrics = GitIntegration._calculate_complexity_metrics(all_files)
        
        # Analyze tech stack
        tech_stack = GitIntegration._analyze_tech_stack(all_files)
        
        print(f"🏗️ Architecture analysis: {len(detected_patterns)} patterns, {len(design_issues)} issues, {len(recommendations)} recommendations")
        
        return ArchitectureAnalysis(
            detected_patterns=detected_patterns,
            project_structure=project_structure,
            design_issues=design_issues,
            recommendations=recommendations,
            complexity_metrics=complexity_metrics,
            tech_stack=tech_stack
        )

    @staticmethod
    def _discover_all_project_files() -> List[str]:
        """Discover all project files using git."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                check=True
            )
            files = [f for f in result.stdout.strip().split('\n') if f and not f.startswith('.')]
            return files[:200]  # Limit to avoid overwhelming analysis
        except subprocess.CalledProcessError:
            return []

    @staticmethod
    def _detect_architecture_patterns(all_files: List[str]) -> List[ArchitecturePattern]:
        """Detect common architecture patterns in the codebase."""
        patterns = []
        file_paths = [f.lower() for f in all_files]
        
        # MVC Pattern Detection
        mvc_evidence = []
        has_models = any('model' in f or '/models/' in f for f in file_paths)
        has_views = any('view' in f or '/views/' in f or 'template' in f for f in file_paths)
        has_controllers = any('controller' in f or '/controllers/' in f for f in file_paths)
        
        if has_models: mvc_evidence.append("Models directory/files detected")
        if has_views: mvc_evidence.append("Views/templates detected")
        if has_controllers: mvc_evidence.append("Controllers detected")
        
        if len(mvc_evidence) >= 2:
            confidence = len(mvc_evidence) / 3.0
            patterns.append(ArchitecturePattern(
                pattern_type="MVC (Model-View-Controller)",
                confidence=confidence,
                evidence=mvc_evidence,
                description="Traditional web application architecture with separated concerns"
            ))

        # Microservices Pattern Detection
        microservices_evidence = []
        has_services = len([f for f in file_paths if 'service' in f]) > 2
        has_api_routes = any('route' in f or 'api' in f for f in file_paths)
        has_docker = any('docker' in f for f in file_paths)
        has_multiple_mains = len([f for f in file_paths if 'main' in f or 'app' in f]) > 1
        
        if has_services: microservices_evidence.append("Multiple service files detected")
        if has_api_routes: microservices_evidence.append("API routes detected")
        if has_docker: microservices_evidence.append("Docker configuration found")
        if has_multiple_mains: microservices_evidence.append("Multiple entry points detected")
        
        if len(microservices_evidence) >= 2:
            confidence = min(len(microservices_evidence) / 4.0, 1.0)
            patterns.append(ArchitecturePattern(
                pattern_type="Microservices",
                confidence=confidence,
                evidence=microservices_evidence,
                description="Distributed architecture with independent deployable services"
            ))

        # Layered Architecture Detection
        layered_evidence = []
        has_data_layer = any(term in f for f in file_paths for term in ['repository', 'dao', 'data', 'persistence'])
        has_business_layer = any(term in f for f in file_paths for term in ['business', 'domain', 'logic'])
        has_presentation_layer = any(term in f for f in file_paths for term in ['presentation', 'ui', 'web'])
        
        if has_data_layer: layered_evidence.append("Data access layer detected")
        if has_business_layer: layered_evidence.append("Business logic layer detected")
        if has_presentation_layer: layered_evidence.append("Presentation layer detected")
        
        if len(layered_evidence) >= 2:
            confidence = len(layered_evidence) / 3.0
            patterns.append(ArchitecturePattern(
                pattern_type="Layered Architecture",
                confidence=confidence,
                evidence=layered_evidence,
                description="Horizontally structured architecture with distinct layers"
            ))

        # Clean Architecture Detection
        clean_evidence = []
        has_entities = any('entit' in f for f in file_paths)
        has_usecases = any('usecase' in f or 'use_case' in f for f in file_paths)
        has_adapters = any('adapter' in f for f in file_paths)
        has_frameworks = any('framework' in f for f in file_paths)
        
        if has_entities: clean_evidence.append("Entities layer detected")
        if has_usecases: clean_evidence.append("Use cases layer detected")
        if has_adapters: clean_evidence.append("Adapters layer detected")
        
        if len(clean_evidence) >= 2:
            confidence = len(clean_evidence) / 3.0
            patterns.append(ArchitecturePattern(
                pattern_type="Clean Architecture",
                confidence=confidence,
                evidence=clean_evidence,
                description="Dependency-inverted architecture focusing on business rules"
            ))

        # Component-Based Architecture (React/Vue/Angular)
        component_evidence = []
        has_components = len([f for f in file_paths if 'component' in f]) > 2
        has_react = any('.jsx' in f or '.tsx' in f for f in all_files)
        has_vue = any('.vue' in f for f in all_files)
        has_angular = any(term in f for f in file_paths for term in ['angular', '.component.ts'])
        
        if has_components: component_evidence.append("Component files detected")
        if has_react: component_evidence.append("React components detected")
        if has_vue: component_evidence.append("Vue components detected")
        if has_angular: component_evidence.append("Angular components detected")
        
        if len(component_evidence) >= 2:
            confidence = len(component_evidence) / 4.0
            patterns.append(ArchitecturePattern(
                pattern_type="Component-Based Frontend",
                confidence=confidence,
                evidence=component_evidence,
                description="Modular frontend architecture with reusable components"
            ))

        return patterns

    @staticmethod
    def _analyze_project_structure(all_files: List[str]) -> Dict[str, List[str]]:
        """Analyze and categorize project structure."""
        structure = {
            "Frontend": [],
            "Backend": [],
            "Database": [],
            "Configuration": [],
            "Tests": [],
            "Documentation": [],
            "Build/Deploy": [],
            "Assets": []
        }
        
        for file_path in all_files:
            file_lower = file_path.lower()
            
            # Frontend files
            if any(ext in file_path for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.scss']):
                structure["Frontend"].append(file_path)
            
            # Backend files
            elif any(ext in file_path for ext in ['.py', '.java', '.go', '.cs', '.php', '.rb']):
                structure["Backend"].append(file_path)
            
            # Database files
            elif any(term in file_lower for term in ['migration', 'seed', '.sql', 'database', 'schema']):
                structure["Database"].append(file_path)
            
            # Configuration files
            elif any(ext in file_path for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.env']):
                structure["Configuration"].append(file_path)
            
            # Test files
            elif any(term in file_lower for term in ['test', 'spec', '__test__', '.test.', '.spec.']):
                structure["Tests"].append(file_path)
            
            # Documentation
            elif any(ext in file_path for ext in ['.md', '.rst', '.txt']) and 'readme' in file_lower:
                structure["Documentation"].append(file_path)
            
            # Build/Deploy files
            elif any(term in file_lower for term in ['dockerfile', 'makefile', 'package.json', 'requirements', 'build', 'deploy']):
                structure["Build/Deploy"].append(file_path)
            
            # Assets
            elif any(ext in file_path for ext in ['.png', '.jpg', '.svg', '.ico', '.gif']):
                structure["Assets"].append(file_path)
        
        # Remove empty categories
        return {k: v for k, v in structure.items() if v}

    @staticmethod
    def _identify_design_issues(all_files: List[str], changed_files: List[str]) -> List[str]:
        """Identify potential architectural design issues."""
        issues = []
        
        # Large file detection
        large_files = []
        for file_path in changed_files:
            try:
                content = GitIntegration.get_file_content(file_path)
                line_count = len(content.split('\n'))
                if line_count > 500:
                    large_files.append(f"{file_path} ({line_count} lines)")
            except:
                continue
        
        if large_files:
            issues.append(f"Large files detected that may need refactoring: {', '.join(large_files[:3])}")
        
        # Circular dependency detection (simplified)
        file_imports = {}
        for file_path in changed_files[:10]:  # Limit analysis
            try:
                context = GitIntegration.get_file_context(file_path)
                file_imports[file_path] = context.imports
            except:
                continue
        
        # Check for potential circular dependencies
        for file_path, imports in file_imports.items():
            for imp in imports:
                if file_path.replace('.py', '').replace('.js', '') in imp:
                    issues.append(f"Potential self-import in {file_path}")
        
        # Missing separation of concerns
        mixed_concerns = []
        for file_path in changed_files:
            file_lower = file_path.lower()
            content = None
            try:
                content = GitIntegration.get_file_content(file_path)
            except:
                continue
                
            if content:
                content_lower = content.lower()
                # Check if single file has database, business logic, and UI concerns
                has_db = any(term in content_lower for term in ['select', 'insert', 'update', 'delete', 'query'])
                has_ui = any(term in content_lower for term in ['render', 'component', 'html', 'css'])
                has_business = any(term in content_lower for term in ['calculate', 'validate', 'process'])
                
                concerns = sum([has_db, has_ui, has_business])
                if concerns >= 2:
                    mixed_concerns.append(file_path)
        
        if mixed_concerns:
            issues.append(f"Mixed concerns detected in: {', '.join(mixed_concerns[:3])}")
        
        # Duplicate code patterns (simplified detection)
        if len(changed_files) > 1:
            similar_functions = []
            all_functions = []
            for file_path in changed_files[:5]:
                try:
                    context = GitIntegration.get_file_context(file_path)
                    for func in context.functions:
                        all_functions.append((file_path, func))
                except:
                    continue
            
            # Look for similar function names
            function_names = [func for _, func in all_functions]
            duplicates = []
            for name in set(function_names):
                if function_names.count(name) > 1:
                    duplicates.append(name)
            
            if duplicates:
                issues.append(f"Potential duplicate function names across files: {', '.join(duplicates[:3])}")
        
        return issues

    @staticmethod
    def _generate_architecture_recommendations(patterns: List[ArchitecturePattern], 
                                             structure: Dict[str, List[str]], 
                                             issues: List[str], 
                                             changed_files: List[str]) -> List[str]:
        """Generate architecture improvement recommendations."""
        recommendations = []
        
        # Pattern-based recommendations
        if not patterns:
            recommendations.append("Consider adopting a clear architectural pattern (MVC, Clean Architecture, or Layered) for better code organization")
        elif len(patterns) > 2:
            recommendations.append("Multiple architectural patterns detected - consider consolidating to a single consistent approach")
        
        # Structure-based recommendations
        if "Tests" not in structure or len(structure.get("Tests", [])) < len(changed_files) * 0.5:
            recommendations.append("Consider increasing test coverage - detected low test file ratio")
        
        if "Documentation" not in structure or len(structure.get("Documentation", [])) == 0:
            recommendations.append("Add architectural documentation (README, design docs) to help new developers understand the system")
        
        frontend_files = structure.get("Frontend", [])
        backend_files = structure.get("Backend", [])
        
        if frontend_files and backend_files and len(frontend_files) > len(backend_files) * 2:
            recommendations.append("Frontend-heavy architecture detected - consider implementing API-first design for better scalability")
        
        # Issue-based recommendations
        if any("Large files" in issue for issue in issues):
            recommendations.append("Break down large files into smaller, more focused modules following Single Responsibility Principle")
        
        if any("Mixed concerns" in issue for issue in issues):
            recommendations.append("Implement proper separation of concerns - separate business logic, data access, and presentation layers")
        
        if any("duplicate" in issue.lower() for issue in issues):
            recommendations.append("Extract common functionality into shared utilities or base classes to reduce duplication")
        
        # Change-specific recommendations
        api_changes = [f for f in changed_files if any(term in f.lower() for term in ['api', 'route', 'endpoint'])]
        if api_changes:
            recommendations.append("API changes detected - ensure backward compatibility and consider API versioning strategy")
        
        database_changes = [f for f in changed_files if any(term in f.lower() for term in ['model', 'migration', 'database'])]
        if database_changes:
            recommendations.append("Database-related changes detected - ensure proper migration strategy and data integrity")
        
        # General best practices
        if len(changed_files) > 10:
            recommendations.append("Large changeset detected - consider breaking into smaller, focused pull requests for easier review")
        
        return recommendations[:8]  # Limit to most important recommendations

    @staticmethod
    def _calculate_complexity_metrics(all_files: List[str]) -> Dict[str, float]:
        """Calculate various complexity metrics."""
        metrics = {
            "total_files": len(all_files),
            "avg_file_size": 0.0,
            "dependency_depth": 0.0,
            "code_to_config_ratio": 0.0
        }
        
        try:
            code_files = [f for f in all_files if any(ext in f for ext in ['.py', '.js', '.java', '.go', '.ts'])]
            config_files = [f for f in all_files if any(ext in f for ext in ['.json', '.yaml', '.yml', '.xml'])]
            
            if code_files:
                total_lines = 0
                valid_files = 0
                
                for file_path in code_files[:20]:  # Sample to avoid performance issues
                    try:
                        content = GitIntegration.get_file_content(file_path)
                        total_lines += len(content.split('\n'))
                        valid_files += 1
                    except:
                        continue
                
                if valid_files > 0:
                    metrics["avg_file_size"] = total_lines / valid_files
            
            if config_files:
                metrics["code_to_config_ratio"] = len(code_files) / len(config_files)
            
            # Simple dependency depth approximation
            metrics["dependency_depth"] = min(len(all_files) / 50.0, 5.0)  # Normalize to 0-5 scale
            
        except Exception:
            pass
        
        return metrics

    @staticmethod
    def _analyze_tech_stack(all_files: List[str]) -> Dict[str, List[str]]:
        """Analyze the technology stack used in the project."""
        tech_stack = {
            "Languages": [],
            "Frameworks": [],
            "Databases": [],
            "Tools": [],
            "Cloud/Infrastructure": []
        }
        
        # Language detection
        extensions = set(Path(f).suffix.lower() for f in all_files)
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        
        for ext, lang in language_map.items():
            if ext in extensions:
                tech_stack["Languages"].append(lang)
        
        # Framework detection based on files/patterns
        file_names = [f.lower() for f in all_files]
        
        # Frontend frameworks
        if any('.jsx' in f or '.tsx' in f for f in all_files) or any('react' in f for f in file_names):
            tech_stack["Frameworks"].append("React")
        if any('.vue' in f for f in all_files):
            tech_stack["Frameworks"].append("Vue.js")
        if any('angular' in f for f in file_names):
            tech_stack["Frameworks"].append("Angular")
        
        # Backend frameworks
        if any('django' in f for f in file_names):
            tech_stack["Frameworks"].append("Django")
        if any('flask' in f for f in file_names):
            tech_stack["Frameworks"].append("Flask")
        if any('spring' in f for f in file_names):
            tech_stack["Frameworks"].append("Spring")
        if any('express' in f for f in file_names):
            tech_stack["Frameworks"].append("Express.js")
        
        # Database detection
        if any('postgres' in f or 'postgresql' in f for f in file_names):
            tech_stack["Databases"].append("PostgreSQL")
        if any('mysql' in f for f in file_names):
            tech_stack["Databases"].append("MySQL")
        if any('mongo' in f for f in file_names):
            tech_stack["Databases"].append("MongoDB")
        if any('redis' in f for f in file_names):
            tech_stack["Databases"].append("Redis")
        
        # Tools detection
        if any('docker' in f for f in file_names):
            tech_stack["Tools"].append("Docker")
        if any('kubernetes' in f or 'k8s' in f for f in file_names):
            tech_stack["Tools"].append("Kubernetes")
        if any('webpack' in f for f in file_names):
            tech_stack["Tools"].append("Webpack")
        if any('jest' in f for f in file_names):
            tech_stack["Tools"].append("Jest")
        
        # Cloud/Infrastructure
        if any('aws' in f for f in file_names):
            tech_stack["Cloud/Infrastructure"].append("AWS")
        if any('gcp' in f or 'google' in f for f in file_names):
            tech_stack["Cloud/Infrastructure"].append("Google Cloud")
        if any('azure' in f for f in file_names):
            tech_stack["Cloud/Infrastructure"].append("Azure")
        
        # Remove empty categories
        return {k: v for k, v in tech_stack.items() if v}

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

    def generate_report(self, reviews: List[CodeReview], output_format: str = "markdown", architecture_analysis: ArchitectureAnalysis = None) -> str:
        """Generate a formatted report of the findings."""
        if output_format == "markdown":
            return self._generate_markdown_report(reviews, architecture_analysis)
        elif output_format == "json":
            return json.dumps([vars(r) for r in reviews], indent=2)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _generate_markdown_report(self, reviews: List[CodeReview], architecture_analysis: ArchitectureAnalysis = None) -> str:
        """Generate an enhanced markdown report with fixes and architecture insights."""
        if not reviews and not architecture_analysis:
            return "# 🤖 AI Code Review Report\n\n✅ **No issues found!** Your code looks great! 🎉"

        # Count issues by severity
        severity_counts = {'critical': 0, 'major': 0, 'minor': 0, 'info': 0}
        for review in reviews:
            severity_counts[review.severity] = severity_counts.get(review.severity, 0) + 1

        report = [
            "# 🤖 AI Code Review Report",
            f"\n📅 **Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📊 **Total findings:** {len(reviews)}",
            "",
            "## 📈 Summary",
            f"- 🔴 **Critical:** {severity_counts['critical']} issues",
            f"- 🟠 **Major:** {severity_counts['major']} issues",
            f"- 🟡 **Minor:** {severity_counts['minor']} issues",
            f"- ℹ️ **Info:** {severity_counts['info']} issues",
            ""
        ]

        # Add architecture analysis section
        if architecture_analysis:
            report.append("## 🏗️ Architecture Analysis")
            report.append("")
            
            # Detected patterns
            if architecture_analysis.detected_patterns:
                report.append("### 📐 Detected Architecture Patterns")
                for pattern in architecture_analysis.detected_patterns:
                    confidence_emoji = "🎯" if pattern.confidence > 0.8 else "🤔" if pattern.confidence > 0.5 else "❓"
                    report.append(f"- {confidence_emoji} **{pattern.pattern_type}** ({pattern.confidence:.0%} confidence)")
                    report.append(f"  - {pattern.description}")
                    if pattern.evidence:
                        report.append(f"  - Evidence: {', '.join(pattern.evidence)}")
                report.append("")
            
            # Tech stack
            if architecture_analysis.tech_stack:
                report.append("### ⚡ Technology Stack")
                for category, technologies in architecture_analysis.tech_stack.items():
                    if technologies:
                        report.append(f"- **{category}:** {', '.join(technologies)}")
                report.append("")
            
            # Project structure
            if architecture_analysis.project_structure:
                report.append("### 📁 Project Structure")
                for layer, files in architecture_analysis.project_structure.items():
                    report.append(f"- **{layer}:** {len(files)} files")
                report.append("")
            
            # Design issues
            if architecture_analysis.design_issues:
                report.append("### ⚠️ Architectural Concerns")
                for issue in architecture_analysis.design_issues:
                    report.append(f"- {issue}")
                report.append("")
            
            # Recommendations
            if architecture_analysis.recommendations:
                report.append("### 💡 Architecture Recommendations")
                for i, rec in enumerate(architecture_analysis.recommendations, 1):
                    report.append(f"{i}. {rec}")
                report.append("")
            
            # Complexity metrics
            if architecture_analysis.complexity_metrics:
                metrics = architecture_analysis.complexity_metrics
                report.append("### 📊 Complexity Metrics")
                if metrics.get('total_files'):
                    report.append(f"- **Total Files:** {int(metrics['total_files'])}")
                if metrics.get('avg_file_size'):
                    report.append(f"- **Average File Size:** {int(metrics['avg_file_size'])} lines")
                if metrics.get('code_to_config_ratio'):
                    report.append(f"- **Code to Config Ratio:** {metrics['code_to_config_ratio']:.1f}:1")
                report.append("")

        # Detailed findings
        if reviews:
            report.append("## 🔍 Detailed Findings")
            report.append("")

        for i, review in enumerate(reviews, 1):
            emoji = {'critical': '🔴', 'major': '🟠', 'minor': '🟡', 'info': 'ℹ️'}[review.severity]
            confidence_emoji = {'high': '🎯', 'medium': '🤔', 'low': '❓'}.get(review.confidence, '🤔')

            report.append(f"### {i}. {emoji} **{review.severity.upper()}** - {review.category}")
            report.append(f"📄 **File:** `{review.file}` (Lines {review.line_start}-{review.line_end}) {confidence_emoji}")
            report.append("")
            report.append(f"💬 **Issue:** {review.message}")

            if review.impact:
                report.append(f"⚠️ **Impact:** {review.impact}")

            if review.suggestion:
                report.append(f"💡 **Suggestion:** {review.suggestion}")
                
            # Add architecture cross-reference for architecture-related issues
            if review.category in ['architecture', 'design-pattern'] and architecture_analysis and architecture_analysis.detected_patterns:
                related_patterns = [p.pattern_type for p in architecture_analysis.detected_patterns]
                if related_patterns:
                    report.append(f"🏗️ **Architecture Context:** This relates to the detected {', '.join(related_patterns)} pattern(s) in your project.")

            if review.code_snippet:
                report.append(f"\n**❌ Current Code:**")
                # Detect language from file extension for better syntax highlighting
                file_ext = review.file.split('.')[-1] if '.' in review.file else ''
                lang_map = {'tsx': 'typescript', 'ts': 'typescript', 'js': 'javascript', 'jsx': 'javascript', 'py': 'python', 'java': 'java', 'go': 'go'}
                lang = lang_map.get(file_ext, '')
                report.append(f"```{lang}")
                report.append(f"{review.code_snippet}")
                report.append(f"```")

            if review.fixed_code:
                report.append(f"\n**✅ Fixed Code:**")
                # Use same language detection for fixed code
                file_ext = review.file.split('.')[-1] if '.' in review.file else ''
                lang_map = {'tsx': 'typescript', 'ts': 'typescript', 'js': 'javascript', 'jsx': 'javascript', 'py': 'python', 'java': 'java', 'go': 'go'}
                lang = lang_map.get(file_ext, '')
                report.append(f"```{lang}")
                report.append(f"{review.fixed_code}")
                report.append(f"```")
                
                # Add implementation steps if this is an architecture fix
                if review.category in ['architecture', 'design-pattern']:
                    report.append(f"\n**🔧 Implementation Steps:**")
                    report.append(f"1. Create the refactored component/function as shown above")
                    report.append(f"2. Update imports in dependent files if needed")
                    report.append(f"3. Test the changes to ensure functionality is preserved")
                    report.append(f"4. Consider updating related documentation")

            if review.confidence:
                report.append(f"\n🎯 **Confidence Level:** {review.confidence}")

            report.append("\n---\n")

        # Add helpful footer
        report.append("## 🚀 Next Steps")
        report.append("")
        report.append("1. Review each finding above")
        report.append("2. Apply the suggested fixes (✅ **Fixed Code** sections)")
        report.append("3. Test your changes thoroughly")
        report.append("4. Re-run the AI code review to verify fixes")
        report.append("")
        report.append("💡 **Tip:** Focus on 🔴 Critical and 🟠 Major issues first!")

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
    report = enforcer.generate_report(reviews, args.output, reviewer.architecture_analysis)
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