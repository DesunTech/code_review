"""
Enhanced configuration management system for AI code review.
Provides validation, defaults, and environment variable support.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator, ValidationError
from dataclasses import dataclass, field
import logging

# Custom exceptions
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class CodeReviewException(Exception):
    """Base exception for code review system."""
    pass

class ProviderException(CodeReviewException):
    """Exception for AI provider issues."""
    pass

class ValidationException(CodeReviewException):
    """Exception for validation errors."""
    pass

# Configuration Models using Pydantic
class CheckConfig(BaseModel):
    """Configuration for individual code checks."""
    name: str
    pattern: str
    severity: str = Field(regex=r'^(critical|major|minor|info)$')
    message: str
    enabled: bool = True

class ComplexityConfig(BaseModel):
    """Configuration for complexity thresholds."""
    cyclomatic_complexity: int = Field(ge=1, le=50, default=10)
    cognitive_complexity: int = Field(ge=1, le=50, default=15)
    max_function_length: int = Field(ge=10, le=1000, default=50)
    max_file_length: int = Field(ge=100, le=10000, default=500)

class LanguageConfig(BaseModel):
    """Configuration for language-specific rules."""
    checks: List[CheckConfig] = Field(default_factory=list)
    complexity: ComplexityConfig = Field(default_factory=ComplexityConfig)

class SecurityConfig(BaseModel):
    """Security-specific configuration."""
    patterns: List[CheckConfig] = Field(default_factory=list)

class PerformanceConfig(BaseModel):
    """Performance-specific configuration."""
    patterns: List[CheckConfig] = Field(default_factory=list)

class ReviewCategoriesConfig(BaseModel):
    """Configuration for review categories."""
    performance: bool = True
    security: bool = True
    style: bool = True
    logic: bool = True
    best_practice: bool = True

class ReviewConfig(BaseModel):
    """Main review configuration."""
    fail_on_severity: str = Field(regex=r'^(critical|major|minor|info)$', default='major')
    max_findings: int = Field(ge=1, le=1000, default=50)
    categories: ReviewCategoriesConfig = Field(default_factory=ReviewCategoriesConfig)

class NamingConventionConfig(BaseModel):
    """Naming convention configuration."""
    functions: str = Field(regex=r'^(camelCase|snake_case|PascalCase)$', default='snake_case')
    variables: str = Field(regex=r'^(camelCase|snake_case)$', default='snake_case')
    constants: str = Field(regex=r'^(UPPER_SNAKE_CASE|camelCase)$', default='UPPER_SNAKE_CASE')
    classes: str = Field(regex=r'^(PascalCase|snake_case)$', default='PascalCase')

class FileStructureConfig(BaseModel):
    """File structure configuration."""
    max_imports: int = Field(ge=5, le=100, default=20)
    import_order: List[str] = Field(default_factory=lambda: ['stdlib', 'third_party', 'local'])

class DocumentationConfig(BaseModel):
    """Documentation requirements configuration."""
    require_function_docs: bool = True
    require_class_docs: bool = True
    min_doc_length: int = Field(ge=5, le=500, default=10)

class StyleConfig(BaseModel):
    """Code style configuration."""
    naming: NamingConventionConfig = Field(default_factory=NamingConventionConfig)
    file_structure: FileStructureConfig = Field(default_factory=FileStructureConfig)
    documentation: DocumentationConfig = Field(default_factory=DocumentationConfig)

class ProviderConfiguration(BaseModel):
    """AI Provider configuration."""
    name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model: str = ""
    max_tokens: int = Field(ge=100, le=8000, default=4000)
    temperature: float = Field(ge=0.0, le=2.0, default=0.1)
    timeout: int = Field(ge=30, le=300, default=120)

class PerformanceSettingsConfig(BaseModel):
    """Performance settings configuration."""
    max_file_size: int = Field(ge=50, le=10000, default=500)  # in KB
    skip_patterns: List[str] = Field(default_factory=lambda: [
        "*.min.js", "*.generated.*", "vendor/*", 
        "node_modules/*", "*.lock", "*.sum"
    ])
    max_diff_lines: int = Field(ge=100, le=50000, default=5000)
    timeout: int = Field(ge=30, le=600, default=120)

class ReportingConfig(BaseModel):
    """Reporting configuration."""
    include_code_snippets: bool = True
    max_snippet_length: int = Field(ge=50, le=1000, default=200)
    group_by: str = Field(regex=r'^(file|severity|category)$', default='file')
    formats: List[str] = Field(default_factory=lambda: ['markdown', 'json'])

class CodeReviewConfig(BaseModel):
    """Main configuration model for the code review system."""
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    languages: Dict[str, LanguageConfig] = Field(default_factory=dict)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    style: StyleConfig = Field(default_factory=StyleConfig)
    custom_rules: List[CheckConfig] = Field(default_factory=list)
    performance_settings: PerformanceSettingsConfig = Field(default_factory=PerformanceSettingsConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    providers: Dict[str, ProviderConfiguration] = Field(default_factory=dict)

    def validate_severity(self, severity: str) -> bool:
        """Validate severity level."""
        return severity in ['critical', 'major', 'minor', 'info']

    def get_severity_weight(self, severity: str) -> int:
        """Get numeric weight for severity."""
        weights = {'critical': 4, 'major': 3, 'minor': 2, 'info': 1}
        return weights.get(severity, 0)

class ConfigManager:
    """Enhanced configuration manager with validation and defaults."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config: Optional[CodeReviewConfig] = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for configuration management."""
        logger = logging.getLogger('config_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_paths = [
            '.ai-code-review.yml',
            '.ai-code-review.yaml',
            'config/ai-code-review.yml',
            os.path.expanduser('~/.ai-code-review.yml'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None
    
    def load_config(self) -> CodeReviewConfig:
        """Load and validate configuration."""
        try:
            if self.config_path and os.path.exists(self.config_path):
                self.logger.info(f"Loading configuration from {self.config_path}")
                config_data = self._load_config_file(self.config_path)
            else:
                self.logger.info("Using default configuration")
                config_data = self._get_default_config()
            
            # Add environment variable overrides
            config_data = self._apply_env_overrides(config_data)
            
            # Validate and create config object
            self.config = CodeReviewConfig(**config_data)
            self.logger.info("Configuration loaded and validated successfully")
            
            return self.config
            
        except ValidationError as e:
            error_msg = f"Configuration validation failed: {e}"
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to load configuration: {e}"
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg) from e
    
    def _load_config_file(self, path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(path, 'r') as f:
                if path.endswith(('.yml', '.yaml')):
                    return yaml.safe_load(f) or {}
                elif path.endswith('.json'):
                    return json.load(f)
                else:
                    # Try to detect format from content
                    content = f.read()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return yaml.safe_load(content) or {}
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file {path}: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "review": {
                "fail_on_severity": "major",
                "max_findings": 50,
                "categories": {
                    "performance": True,
                    "security": True,
                    "style": True,
                    "logic": True,
                    "best_practice": True
                }
            },
            "providers": {
                "claude": {
                    "name": "claude",
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                "openai": {
                    "name": "openai",
                    "model": "gpt-4-turbo-preview",
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                "openrouter": {
                    "name": "openrouter",
                    "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                    "model": "openai/gpt-4-turbo-preview",
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                "local": {
                    "name": "local",
                    "endpoint": "http://localhost:11434/api/generate",
                    "model": "codellama",
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            },
            "security": {
                "patterns": [
                    {
                        "name": "SQL Injection",
                        "pattern": "(SELECT|INSERT|UPDATE|DELETE).+\\+.+(\\w+|\\]|\\))",
                        "severity": "critical",
                        "message": "Potential SQL injection vulnerability. Use parameterized queries"
                    },
                    {
                        "name": "Hardcoded secrets",
                        "pattern": "(api_key|apikey|password|secret|token)\\s*=\\s*[\"'][^\"']+[\"']",
                        "severity": "critical",
                        "message": "Avoid hardcoding secrets. Use environment variables"
                    }
                ]
            }
        }
    
    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # Provider API keys
        env_mappings = {
            'ANTHROPIC_API_KEY': ['providers', 'claude', 'api_key'],
            'OPENAI_API_KEY': ['providers', 'openai', 'api_key'],
            'OPENROUTER_API_KEY': ['providers', 'openrouter', 'api_key'],
            'CODE_REVIEW_FAIL_ON': ['review', 'fail_on_severity'],
            'CODE_REVIEW_MAX_FINDINGS': ['review', 'max_findings'],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Navigate to the nested dictionary and set the value
                current = config_data
                for key in config_path[:-1]:
                    current = current.setdefault(key, {})
                
                # Convert to appropriate type
                if config_path[-1] == 'max_findings':
                    value = int(value)
                    
                current[config_path[-1]] = value
        
        return config_data
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        if not self.config:
            raise ConfigurationError("No configuration to save")
        
        save_path = path or self.config_path or '.ai-code-review.yml'
        
        try:
            config_dict = self.config.dict()
            with open(save_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            error_msg = f"Failed to save configuration: {e}"
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg) from e
    
    def validate_config(self, config_dict: Dict[str, Any]) -> bool:
        """Validate configuration dictionary."""
        try:
            CodeReviewConfig(**config_dict)
            return True
        except ValidationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfiguration]:
        """Get configuration for specific provider."""
        if not self.config:
            self.load_config()
        
        return self.config.providers.get(provider_name)
    
    def add_custom_rule(self, name: str, pattern: str, severity: str, message: str) -> None:
        """Add a custom rule to the configuration."""
        if not self.config:
            self.load_config()
        
        rule = CheckConfig(
            name=name,
            pattern=pattern,
            severity=severity,
            message=message
        )
        
        self.config.custom_rules.append(rule)
        self.logger.info(f"Added custom rule: {name}")

# Rate limiting and security utilities
class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire a rate limit slot."""
        import time
        now = time.time()
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.requests.append(now)

class InputValidator:
    """Validate and sanitize input data."""
    
    @staticmethod
    def validate_diff_content(diff_content: str) -> str:
        """Validate and sanitize diff content."""
        if not diff_content or not isinstance(diff_content, str):
            raise ValidationException("Invalid diff content")
        
        # Basic sanitization
        if len(diff_content) > 100000:  # 100KB limit
            raise ValidationException("Diff content too large")
        
        return diff_content.strip()
    
    @staticmethod
    def validate_context(context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and sanitize context data."""
        if context is None:
            return {}
        
        if not isinstance(context, dict):
            raise ValidationException("Context must be a dictionary")
        
        # Sanitize known fields
        allowed_fields = {'language', 'project_type', 'branch', 'author'}
        sanitized = {}
        
        for key, value in context.items():
            if key in allowed_fields and isinstance(value, str):
                sanitized[key] = value[:100]  # Limit string length
        
        return sanitized

# Example usage and testing
if __name__ == "__main__":
    # Test configuration loading and validation
    config_manager = ConfigManager()
    
    try:
        config = config_manager.load_config()
        print("✓ Configuration loaded successfully")
        print(f"Fail on severity: {config.review.fail_on_severity}")
        print(f"Max findings: {config.review.max_findings}")
        print(f"Available providers: {list(config.providers.keys())}")
        
    except ConfigurationError as e:
        print(f"✗ Configuration error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
