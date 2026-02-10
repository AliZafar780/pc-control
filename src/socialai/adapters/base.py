"""
Base Adapter for Social Media Platforms

Abstract base class that defines the interface for all social media adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse
import aiohttp
import asyncio


@dataclass
class EngagementMetrics:
    """Social media engagement metrics."""
    likes: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    views: Optional[int] = None
    retweets: Optional[int] = None
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None
    bookmarks: Optional[int] = None


@dataclass
class Post:
    """Standardized social media post representation."""
    id: str
    content: str
    title: Optional[str] = None
    author: str = ""
    author_id: Optional[str] = None
    platform: str = ""
    url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Content metadata
    media_urls: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    language: Optional[str] = None
    
    # Engagement
    metrics: Optional[EngagementMetrics] = None
    engagement_score: Optional[float] = None
    
    # Platform-specific fields
    platform_data: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    is_thread: bool = False
    is_reply: bool = False
    reply_to_id: Optional[str] = None
    is_edited: bool = False
    
    # AI-generated fields
    summary: Optional[str] = None
    key_topics: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    
    @property
    def is_long_content(self) -> bool:
        """Check if content is considered long (1000+ characters)."""
        return len(self.content) > 1000
    
    @property
    def reading_time_minutes(self) -> int:
        """Estimate reading time in minutes (200 words per minute)."""
        words = len(self.content.split())
        return max(1, words // 200)
    
    @property
    def has_media(self) -> bool:
        """Check if post contains media content."""
        return len(self.media_urls) > 0
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement (likes + comments + shares)."""
        if not self.metrics:
            return 0
        
        return sum([
            self.metrics.likes or 0,
            self.metrics.comments or 0,
            self.metrics.shares or 0,
            self.metrics.retweets or 0,
            self.metrics.upvotes or 0
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "author": self.author,
            "author_id": self.author_id,
            "platform": self.platform,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "media_urls": self.media_urls,
            "tags": self.tags,
            "language": self.language,
            "metrics": {
                "likes": self.metrics.likes if self.metrics else None,
                "shares": self.metrics.shares if self.metrics else None,
                "comments": self.metrics.comments if self.metrics else None,
                "views": self.metrics.views if self.metrics else None,
                "retweets": self.metrics.retweets if self.metrics else None,
                "upvotes": self.metrics.upvotes if self.metrics else None,
                "downvotes": self.metrics.downvotes if self.metrics else None,
                "bookmarks": self.metrics.bookmarks if self.metrics else None,
            },
            "engagement_score": self.engagement_score,
            "platform_data": self.platform_data,
            "is_thread": self.is_thread,
            "is_reply": self.is_reply,
            "reply_to_id": self.reply_to_id,
            "is_edited": self.is_edited,
            "summary": self.summary,
            "key_topics": self.key_topics,
            "sentiment": self.sentiment,
            "categories": self.categories,
            "reading_time_minutes": self.reading_time_minutes,
            "has_media": self.has_media,
            "total_engagement": self.total_engagement,
        }


class BaseAdapter(ABC):
    """
    Abstract base class for all social media platform adapters.
    
    Each adapter must implement the methods defined here to provide
    a consistent interface for fetching and processing social media content.
    """
    
    platform_name: str = "base"
    supports_search: bool = True
    supports_threads: bool = True
    supports_direct_urls: bool = True
    
    def __init__(self, config: 'Config'):
        """Initialize the adapter with configuration."""
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 1.0  # seconds between requests
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def fetch_feed(self, limit: int = 20, **kwargs) -> List[Post]:
        """
        Fetch posts from the user's feed.
        
        Args:
            limit: Maximum number of posts to fetch
            **kwargs: Platform-specific parameters
        
        Returns:
            List of standardized Post objects
        """
        pass
    
    @abstractmethod
    async def get_post(self, post_id: str) -> Optional[Post]:
        """
        Fetch a specific post by ID.
        
        Args:
            post_id: Platform-specific post identifier
        
        Returns:
            Post object or None if not found
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Post]:
        """
        Search for posts containing the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            **kwargs: Platform-specific search parameters
        
        Returns:
            List of matching Post objects
        """
        pass
    
    async def extract_content_from_url(self, url: str) -> Optional[Post]:
        """
        Extract content from a URL if supported.
        
        Args:
            url: Full URL to a post
        
        Returns:
            Post object or None if URL not supported
        """
        if not self.supports_direct_urls:
            return None
        
        # Parse URL to extract platform-specific information
        parsed = urlparse(url)
        if not self._is_supported_url(url):
            return None
        
        # Extract post ID from URL
        post_id = self._extract_post_id_from_url(url)
        if not post_id:
            return None
        
        return await self.get_post(post_id)
    
    def _is_supported_url(self, url: str) -> bool:
        """
        Check if URL is supported by this adapter.
        
        Override this method in platform-specific adapters.
        """
        return False
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract post ID from URL.
        
        Override this method in platform-specific adapters.
        """
        return None
    
    async def get_thread(self, post_id: str, max_replies: int = 10) -> List[Post]:
        """
        Get a thread starting from a specific post.
        
        Args:
            post_id: Starting post ID
            max_replies: Maximum number of replies to fetch
        
        Returns:
            List of posts in the thread
        """
        if not self.supports_threads:
            return []
        
        posts = []
        current_post = await self.get_post(post_id)
        
        if current_post:
            posts.append(current_post)
            
            # Fetch replies (platform-specific implementation)
            replies = await self._fetch_replies(post_id, max_replies)
            posts.extend(replies)
        
        return posts
    
    async def _fetch_replies(self, post_id: str, max_replies: int) -> List[Post]:
        """
        Fetch replies to a post.
        
        Override this method in platform-specific adapters if needed.
        """
        return []
    
    async def _rate_limited_request(self, coro):
        """Make a rate-limited request."""
        await asyncio.sleep(self.rate_limit_delay)
        return await coro
    
    async def _safe_request(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make a safe HTTP request with error handling.
        
        Args:
            url: Request URL
            **kwargs: Request parameters
        
        Returns:
            Response data or None if request failed
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limited - wait and retry
                    await asyncio.sleep(60)
                    return await self._safe_request(url, **kwargs)
                else:
                    return None
        except Exception:
            return None
    
    def _calculate_engagement_score(self, metrics: Optional[EngagementMetrics]) -> float:
        """
        Calculate an engagement score for a post (0-10 scale).
        
        Args:
            metrics: Engagement metrics
        
        Returns:
            Engagement score from 0 to 10
        """
        if not metrics:
            return 5.0  # Default score
        
        # Base score
        score = 5.0
        
        # Engagement factors
        factors = {
            'likes': 0.001,
            'comments': 0.005,
            'shares': 0.01,
            'views': 0.0001,
            'retweets': 0.008,
            'upvotes': 0.002,
            'downvotes': -0.001,
            'bookmarks': 0.005
        }
        
        total_adjustment = 0.0
        
        for metric_name, weight in factors.items():
            value = getattr(metrics, metric_name, None)
            if value and value > 0:
                if metric_name == 'downvotes':
                    total_adjustment -= weight * value
                else:
                    total_adjustment += weight * value
        
        # Apply adjustments with logarithmic scaling
        import math
        score += math.log(1 + total_adjustment * 1000)
        
        # Clamp to 0-10 range
        return max(0.0, min(10.0, score))
    
    def _sanitize_content(self, content: str) -> str:
        """
        Sanitize content for safe display.
        
        Args:
            content: Raw content
        
        Returns:
            Sanitized content
        """
        # Basic sanitization - remove excessive whitespace
        lines = content.split('\n')
        sanitized_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                sanitized_lines.append(line)
        
        return '\n'.join(sanitized_lines)
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        Extract hashtags/mentions from content.
        
        Args:
            content: Post content
        
        Returns:
            List of extracted tags
        """
        tags = []
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', content)
        tags.extend(hashtags)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', content)
        tags.extend(mentions)
        
        return list(set(tags))  # Remove duplicates
    
    def _truncate_content(self, content: str, max_length: int = 280) -> str:
        """
        Truncate content to specified length.
        
        Args:
            content: Content to truncate
            max_length: Maximum length
        
        Returns:
            Truncated content with ellipsis if needed
        """
        if len(content) <= max_length:
            return content
        
        return content[:max_length-3] + "..."


# Forward reference for type hint
from socialai.config import Config
