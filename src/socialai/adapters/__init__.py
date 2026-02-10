"""
Social Media Adapters

Platform-specific adapters for fetching and processing social media content.
"""

from .base import BaseAdapter, Post, EngagementMetrics
from .registry import AdapterRegistry

__all__ = ['BaseAdapter', 'Post', 'EngagementMetrics', 'AdapterRegistry']
