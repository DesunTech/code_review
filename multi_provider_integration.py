"""
Multi-provider AI integration for code review system.
Supports Claude (Anthropic), GPT-4 (OpenAI), OpenRouter, and local models.
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import aiohttp
from dataclasses import dataclass
from anthropic import Anthropic

# Import custom exceptions
class ProviderException(Exception):
    """Exception for AI provider issues."""
    pass

@dataclass
class ProviderConfig:
    """Configuration for AI providers."""
    name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model: str = ""
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 120

class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Send prompt to AI and return response."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        pass

class ClaudeProvider(AIProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = Anthropic(api_key=config.api_key or os.getenv('ANTHROPIC_API_KEY'))

    async def complete(self, prompt: str) -> str:
        """Send prompt to Claude API."""
        try:
            # Using sync client in async context - in production, use async client
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.config.model or "claude-3-opus-20240229",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise ProviderException(f"Claude API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate Claude configuration."""
        return bool(self.config.api_key or os.getenv('ANTHROPIC_API_KEY'))

class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        from openai import OpenAI
        self.client = OpenAI(api_key=config.api_key or os.getenv('OPENAI_API_KEY'))

    async def complete(self, prompt: str) -> str:
        """Send prompt to OpenAI API."""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config.model or "gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ProviderException(f"OpenAI API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return bool(self.config.api_key or os.getenv('OPENAI_API_KEY'))

class OpenRouterProvider(AIProvider):
    """OpenRouter AI provider using OpenAI-compatible API."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # OpenRouter uses OpenAI-compatible API
        self.api_key = config.api_key or os.getenv('OPENROUTER_API_KEY')
        self.endpoint = config.endpoint or "https://openrouter.ai/api/v1/chat/completions"

    async def complete(self, prompt: str) -> str:
        """Send prompt to OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Optional: for analytics
            "X-Title": "AI Code Reviewer"  # Optional: for analytics
        }

        data = {
            "model": self.config.model or "openai/gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter API error {response.status}: {error_text}")
        except Exception as e:
            raise ProviderException(f"OpenRouter error: {e}")

    def validate_config(self) -> bool:
        return bool(self.api_key)

class LocalModelProvider(AIProvider):
    """Local model provider (Ollama, llama.cpp, etc.)."""

    async def complete(self, prompt: str) -> str:
        """Send prompt to local model endpoint."""
        if not self.config.endpoint:
            raise Exception("No endpoint configured for local model")

        # Ollama API format
        data = {
            "model": self.config.model or "codellama",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.endpoint,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '')
                    else:
                        error_text = await response.text()
                        raise Exception(f"Local model error {response.status}: {error_text}")
        except Exception as e:
            raise ProviderException(f"Local model error: {e}")

    def validate_config(self) -> bool:
        """Validate local model configuration."""
        return bool(self.config.endpoint)

class CustomProvider(AIProvider):
    """Custom provider for enterprise AI services."""

    async def complete(self, prompt: str) -> str:
        """Send prompt to custom endpoint."""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "model": self.config.model
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.endpoint,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('text', data.get('response', ''))
                else:
                    raise Exception(f"Custom provider error: {response.status}")

    def validate_config(self) -> bool:
        """Validate custom provider configuration."""
        return bool(self.config.endpoint and self.config.api_key)

class ProviderFactory:
    """Factory for creating AI providers."""

    providers = {
        'claude': ClaudeProvider,
        'openai': OpenAIProvider,
        'local': LocalModelProvider,
        'custom': CustomProvider,
        'openrouter': OpenRouterProvider
    }

    @classmethod
    def create(cls, provider_type: str, config: ProviderConfig) -> AIProvider:
        """Create a provider instance."""
        provider_class = cls.providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")

        provider = provider_class(config)
        if not provider.validate_config():
            raise ValueError(f"Invalid configuration for {provider_type}")

        return provider

class MultiProviderReviewer:
    """Code reviewer that can use multiple AI providers."""

    def __init__(self, primary_provider: str = "claude", fallback_providers: List[str] = None):
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or ["openai", "local", "openrouter"]
        self.providers: Dict[str, AIProvider] = {}
        self._load_providers()

    def _load_providers(self):
        """Load configured providers."""
        # Load from environment or config file or use defaults
        config_file = os.getenv('AI_PROVIDERS_CONFIG')

        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = json.load(f)
        else:
            # Default configurations
            configs = {
                'claude': {
                    'model': 'claude-3-opus-20240229',
                    'max_tokens': 4000
                },
                'openai': {
                    'model': 'gpt-4-turbo-preview',
                    'max_tokens': 4000
                },
                'openrouter': {
                    'endpoint': 'https://openrouter.ai/api/v1/chat/completions',
                    'model': 'openai/gpt-4-turbo-preview',
                    'max_tokens': 4000
                },
                'local': {
                    'endpoint': 'http://localhost:11434/api/generate',
                    'model': 'codellama',
                    'max_tokens': 2000
                }
            }

        # Create provider instances
        for provider_name, config_dict in configs.items():
            try:
                config = ProviderConfig(name=provider_name, **config_dict)
                provider = ProviderFactory.create(provider_name, config)
                self.providers[provider_name] = provider
                print(f"✓ Loaded provider: {provider_name}")
            except Exception as e:
                print(f"✗ Failed to load provider {provider_name}: {e}")

    async def review_code(self, diff_content: str, context: Dict[str, Any] = None) -> str:
        """Review code using available providers with fallback support."""
        prompt = self._create_prompt(diff_content, context)

        # Try primary provider first
        if self.primary_provider in self.providers:
            try:
                print(f"Using primary provider: {self.primary_provider}")
                return await self.providers[self.primary_provider].complete(prompt)
            except Exception as e:
                print(f"Primary provider failed: {e}")

        # Try fallback providers
        for fallback in self.fallback_providers:
            if fallback in self.providers:
                try:
                    print(f"Using fallback provider: {fallback}")
                    return await self.providers[fallback].complete(prompt)
                except Exception as e:
                    print(f"Fallback provider {fallback} failed: {e}")

        raise ProviderException("All AI providers failed")

    def _create_prompt(self, diff_content: str, context: Dict[str, Any] = None) -> str:
        """Create review prompt."""
        return f"""You are an expert code reviewer. Review this code diff and provide findings in JSON format.

Focus on:
- Performance issues
- Security vulnerabilities
- Logic errors
- Best practices

Code diff:
```diff
{diff_content}
```

Respond with a JSON array of findings. Each finding must have: severity, category, file, line_start, line_end, message, and optional suggestion."""

class ProviderBenchmark:
    """Benchmark different AI providers for code review quality."""

    def __init__(self, providers: List[str]):
        self.providers = providers
        self.results = {}

    async def benchmark(self, test_cases: List[Dict[str, str]]):
        """Run benchmark on test cases."""
        reviewer = MultiProviderReviewer()

        for test_case in test_cases:
            diff = test_case['diff']
            expected_issues = test_case.get('expected_issues', [])

            for provider_name in self.providers:
                if provider_name not in reviewer.providers:
                    continue

                try:
                    start_time = asyncio.get_event_loop().time()
                    response = await reviewer.providers[provider_name].complete(
                        reviewer._create_prompt(diff, None)
                    )
                    end_time = asyncio.get_event_loop().time()

                    # Parse and evaluate response
                    findings = self._parse_findings(response)

                    # Calculate metrics
                    metrics = {
                        'response_time': end_time - start_time,
                        'findings_count': len(findings),
                        'accuracy': self._calculate_accuracy(findings, expected_issues),
                        'false_positives': self._count_false_positives(findings, expected_issues)
                    }

                    if provider_name not in self.results:
                        self.results[provider_name] = []
                    self.results[provider_name].append(metrics)

                except Exception as e:
                    print(f"Benchmark failed for {provider_name}: {e}")

    def _parse_findings(self, response: str) -> List[Dict]:
        """Parse findings from response."""
        try:
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            return json.loads(response.strip())
        except:
            return []

    def _calculate_accuracy(self, findings: List[Dict], expected: List[str]) -> float:
        """Calculate accuracy of findings."""
        if not expected:
            return 1.0 if not findings else 0.0

        found_issues = [f['message'] for f in findings]
        correct = sum(1 for exp in expected if any(exp in found for found in found_issues))
        return correct / len(expected)

    def _count_false_positives(self, findings: List[Dict], expected: List[str]) -> int:
        """Count false positive findings."""
        found_issues = [f['message'] for f in findings]
        return sum(1 for found in found_issues if not any(exp in found for exp in expected))

    def generate_report(self) -> str:
        """Generate benchmark report."""
        report = ["# AI Provider Benchmark Report\n"]

        for provider, metrics_list in self.results.items():
            if not metrics_list:
                continue

            avg_time = sum(m['response_time'] for m in metrics_list) / len(metrics_list)
            avg_accuracy = sum(m['accuracy'] for m in metrics_list) / len(metrics_list)
            total_findings = sum(m['findings_count'] for m in metrics_list)
            total_false_positives = sum(m['false_positives'] for m in metrics_list)

            report.append(f"\n## {provider.capitalize()}")
            report.append(f"- Average response time: {avg_time:.2f}s")
            report.append(f"- Average accuracy: {avg_accuracy:.1%}")
            report.append(f"- Total findings: {total_findings}")
            report.append(f"- False positives: {total_false_positives}")

        return "\n".join(report)

# Example usage
async def main():
    """Example usage of multi-provider system."""
    # Create reviewer with fallback support
    reviewer = MultiProviderReviewer(
        primary_provider="claude",
        fallback_providers=["openai", "local"]
    )

    # Sample diff
    diff = """
+def calculate_user_score(user_id):
+    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
+    score = 0
+    for i in range(len(user.purchases)):
+        score = score + user.purchases[i].amount
+    return score
    """

    # Review code
    try:
        result = await reviewer.review_code(diff, {'language': 'python'})
        print("\nReview Results:")
        print(result)
    except Exception as e:
        print(f"Review failed: {e}")

    # Run benchmark
    print("\n" + "="*50 + "\nRunning Provider Benchmark\n" + "="*50)

    benchmark = ProviderBenchmark(['claude', 'openai', 'local'])

    test_cases = [
        {
            'diff': diff,
            'expected_issues': ['SQL injection', 'inefficient loop']
        }
    ]

    await benchmark.benchmark(test_cases)
    print(benchmark.generate_report())

if __name__ == "__main__":
    asyncio.run(main())