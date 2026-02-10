"""
SocialAI - Distraction-Free AI-Powered Social Media CLI

A modern CLI tool for consuming social media content with AI-powered
summarization, content filtering, and focus modes.
"""

__version__ = "1.0.0"
__author__ = "Ali Zafar"
__license__ = "MIT"

from socialai.config import Config
from socialai.ai import AIService
from socialai.cli import cli

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Config",
    "AIService",
    "cli",
]
