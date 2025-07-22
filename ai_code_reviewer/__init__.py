"""
AI Code Reviewer - Multi-provider AI code review tool
"""

from .ai_code_reviewer import main, cli_main, AICodeReviewer
from .multi_provider_integration import MultiProviderReviewer, ProviderConfig
from .config_manager import ConfigManager

__version__ = "1.0.0"
__all__ = ["main", "cli_main", "AICodeReviewer", "MultiProviderReviewer", "ProviderConfig", "ConfigManager"]
