#!/usr/bin/env python3
"""
Setup script for AI Code Reviewer - Standalone CLI tool for code review.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-code-reviewer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered code review tool with multi-provider support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-code-reviewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "ollama": [
            "ollama-python>=0.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-code-reviewer=ai_code_reviewer:cli_main",
            "code-review=ai_code_reviewer:cli_main",  # Shorter alias
        ],
    },
    keywords="ai, code-review, static-analysis, claude, openai, github-actions, code-quality",
    project_urls={
        "Bug Reports": "https://github.com/your-username/ai-code-reviewer/issues",
        "Source": "https://github.com/your-username/ai-code-reviewer",
        "Documentation": "https://github.com/your-username/ai-code-reviewer/blob/main/PROVIDER_SETUP.md",
    },
    include_package_data=True,
    package_data={
        "ai_code_reviewer": [
            "config/*.yml",
            "config/*.yaml",
            "templates/*.md",
        ],
    },
)