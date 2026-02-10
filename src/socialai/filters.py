"""
Content Filtering

Provides content filtering functionality for distraction-free reading.
"""

import re
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass

from socialai.config import Config
from socialai.adapters.base import Post


@dataclass
class FilterRule:
    """Represents a content filtering rule."""
    type: str  # keyword, sentiment, topic, author
    action: str  # hide, show, flag
    value: str
    case_sensitive: bool = False


class ContentFilter:
    """Filters content based on configurable rules."""
    
    def __init__(self, config: Config):
        self.config = config
        self.rules: List[FilterRule] = self._load_rules()
        self._blocked_keywords: Set[str] = set()
        self._blocked_authors: Set[str] = set()
        self._blocked_topics: Set[str] = set()
        self._initialize_filters()
    
    def _load_rules(self) -> List[FilterRule]:
        """Load filter rules from configuration."""
        rules = []
        filter_config = self.config.focus.content_filter
        
        if not filter_config:
            return rules
        
        for rule_data in filter_config:
            rule = FilterRule(
                type=rule_data.get('type', 'keyword'),
                action=rule_data.get('action', 'hide'),
                value=rule_data.get('value', ''),
                case_sensitive=rule_data.get('case_sensitive', False)
            )
            rules.append(rule)
        
        return rules
    
    def _initialize_filters(self) -> None:
        """Initialize filter sets from rules."""
        for rule in self.rules:
            if rule.type == 'keyword':
                self._blocked_keywords.add(rule.value.lower())
            elif rule.type == 'author':
                self._blocked_authors.add(rule.value.lower())
            elif rule.type == 'topic':
                self._blocked_topics.add(rule.value.lower())
    
    async def apply(self, posts: List[Post], filter_type: str = 'default') -> List[Post]:
        """
        Apply filters to a list of posts.
        
        Args:
            posts: List of posts to filter
            filter_type: Type of filter to apply
        
        Returns:
            Filtered list of posts
        """
        filtered = []
        
        for post in posts:
            if self._should_include(post, filter_type):
                filtered.append(post)
        
        return filtered
    
    def _should_include(self, post: Post, filter_type: str) -> bool:
        """Determine if a post should be included."""
        
        # Check keyword filters
        if self._contains_blocked_keyword(post.content):
            return False
        
        # Check author filters
        if post.author.lower() in self._blocked_authors:
            return False
        
        # Check topic filters
        if self._matches_blocked_topic(post):
            return False
        
        # Apply filter type specific logic
        if filter_type == 'positive':
            return self._is_positive_sentiment(post)
        elif filter_type == 'negative':
            return not self._is_positive_sentiment(post)
        elif filter_type == 'high_engagement':
            return post.engagement_score and post.engagement_score >= 7.0
        elif filter_type == 'low_engagement':
            return not post.engagement_score or post.engagement_score < 5.0
        elif filter_type == 'technical':
            return self._is_technical_content(post)
        elif filter_type == 'news':
            return self._is_news_content(post)
        
        return True
    
    def _contains_blocked_keyword(self, content: str) -> bool:
        """Check if content contains blocked keywords."""
        content_lower = content.lower()
        
        for keyword in self._blocked_keywords:
            if keyword in content_lower:
                return True
        
        return False
    
    def _matches_blocked_topic(self, post: Post) -> bool:
        """Check if post matches blocked topics."""
        content = (post.content + ' ' + (post.title or '')).lower()
        
        for topic in self._blocked_topics:
            if topic in content:
                return True
        
        return False
    
    def _is_positive_sentiment(self, post: Post) -> bool:
        """Simple sentiment analysis (heuristic-based)."""
        if post.sentiment:
            return post.sentiment.lower() in ['positive', 'happy', 'excited']
        
        # Heuristic: Check for positive indicators
        positive_words = ['great', 'awesome', 'amazing', 'love', 'excellent', 'fantastic', 'wonderful']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst', 'poor']
        
        content_lower = post.content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        return positive_count > negative_count
    
    def _is_technical_content(self, post: Post) -> bool:
        """Check if content is technical in nature."""
        technical_keywords = [
            'code', 'programming', 'software', 'api', 'database', 'algorithm',
            'function', 'class', 'implementation', 'architecture', 'framework',
            'library', 'package', 'module', 'debug', 'deploy', 'build', 'test'
        ]
        
        content_lower = (post.content + ' ' + (post.title or '')).lower()
        
        return any(keyword in content_lower for keyword in technical_keywords)
    
    def _is_news_content(self, post: Post) -> bool:
        """Check if content is news-related."""
        news_keywords = [
            'announced', 'released', 'update', 'news', 'report', 'breaking',
            'according to', 'sources say', 'official', 'launch', 'introducing'
        ]
        
        content_lower = (post.content + ' ' + (post.title or '')).lower()
        
        return any(keyword in content_lower for keyword in news_keywords)
    
    def add_rule(self, rule: FilterRule) -> None:
        """Add a new filter rule."""
        self.rules.append(rule)
        
        # Update filter sets
        if rule.type == 'keyword':
            self._blocked_keywords.add(rule.value.lower())
        elif rule.type == 'author':
            self._blocked_authors.add(rule.value.lower())
        elif rule.type == 'topic':
            self._blocked_topics.add(rule.value.lower())
    
    def remove_rule(self, rule_type: str, value: str) -> bool:
        """Remove a filter rule."""
        for i, rule in enumerate(self.rules):
            if rule.type == rule_type and rule.value.lower() == value.lower():
                self.rules.pop(i)
                self._initialize_filters()  # Rebuild filter sets
                return True
        
        return False
    
    def list_rules(self) -> List[Dict[str, str]]:
        """List all active filter rules."""
        return [
            {
                'type': rule.type,
                'action': rule.action,
                'value': rule.value,
                'case_sensitive': rule.case_sensitive
            }
            for rule in self.rules
        ]
    
    def get_statistics(self) -> Dict[str, int]:
        """Get filter statistics."""
        return {
            'total_rules': len(self.rules),
            'blocked_keywords': len(self._blocked_keywords),
            'blocked_authors': len(self._blocked_authors),
            'blocked_topics': len(self._blocked_topics),
        }


class FocusModeFilter:
    """Specialized filter for distraction-free focus mode."""
    
    # Patterns to hide in focus mode
    ENGAGEMENT_PATTERNS = [
        r'\d+ likes',
        r'\d+ hearts',
        r'\d+ claps',
        r'\d+ shares',
        r'\d+ retweets',
        r'\d+ comments',
        r'\d+ replies',
        r'View \d+ replies',
        r'Show more',
        r'Promoted',
        r'Sponsored',
    ]
    
    SOCIAL_PATTERNS = [
        r'@[\w]+',  # Mentions (can keep for context)
        r'#[\w]+',  # Hashtags (can keep for context)
    ]
    
    def __init__(self, hide_engagement: bool = True, hide_comments: bool = True):
        self.hide_engagement = hide_engagement
        self.hide_comments = hide_comments
    
    def filter_content(self, content: str) -> str:
        """Filter content for focus mode."""
        filtered = content
        
        if self.hide_engagement:
            for pattern in self.ENGAGEMENT_PATTERNS:
                filtered = re.sub(pattern, '[hidden]', filtered, flags=re.IGNORECASE)
        
        if self.hide_comments:
            # Remove comment sections
            filtered = re.sub(r'💬.*', '', filtered)
        
        return filtered.strip()
    
    def estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes."""
        words = len(content.split())
        return max(1, words // 200)  # 200 words per minute


class EngagementFilter:
    """Filter posts based on engagement metrics."""
    
    def __init__(
        self,
        min_likes: Optional[int] = None,
        min_shares: Optional[int] = None,
        min_comments: Optional[int] = None,
        min_score: Optional[float] = None
    ):
        self.min_likes = min_likes
        self.min_shares = min_shares
        self.min_comments = min_comments
        self.min_score = min_score
    
    def matches(self, post: Post) -> bool:
        """Check if post meets engagement criteria."""
        if not post.metrics:
            return self.min_score is None
        
        if self.min_likes and (not post.metrics.likes or post.metrics.likes < self.min_likes):
            return False
        
        if self.min_shares and (not post.metrics.shares or post.metrics.shares < self.min_shares):
            return False
        
        if self.min_comments and (not post.metrics.comments or post.metrics.comments < self.min_comments):
            return False
        
        if self.min_score and (not post.engagement_score or post.engagement_score < self.min_score):
            return False
        
        return True
    
    async def apply(self, posts: List[Post]) -> List[Post]:
        """Apply engagement filter to posts."""
        return [post for post in posts if self.matches(post)]
