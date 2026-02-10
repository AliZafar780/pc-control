"""
Basic tests for SocialAI CLI.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone


class TestValidators:
    """Test input validation functions."""
    
    def test_validate_url_valid(self):
        from socialai.utils.validators import validate_url
        assert validate_url("https://twitter.com/user/status/123")
        assert validate_url("https://reddit.com/r/python/comments/abc")
    
    def test_validate_url_invalid(self):
        from socialai.utils.validators import validate_url
        assert not validate_url("not-a-url")
        assert not validate_url("")
    
    def test_validate_platform(self):
        from socialai.utils.validators import validate_platform
        assert validate_platform("twitter")
        assert validate_platform("reddit")
        assert not validate_platform("invalid_platform")
    
    def test_validate_email(self):
        from socialai.utils.validators import validate_email
        assert validate_email("test@example.com")
        assert not validate_email("invalid-email")


class TestFormatters:
    """Test output formatting functions."""
    
    def test_format_post_minimal(self):
        from socialai.adapters.base import Post, EngagementMetrics
        from socialai.utils.formatters import format_post
        
        post = Post(
            id="test_1",
            content="Test content for formatting",
            author="test_user",
            platform="twitter",
            metrics=EngagementMetrics(likes=10, comments=5)
        )
        
        formatted = format_post(post, minimal=True)
        assert "test_user" in formatted
        assert "twitter" in formatted.lower()
    
    def test_wrap_text(self):
        from socialai.utils.formatters import _wrap_text
        
        text = "This is a long text that needs to be wrapped to a specific width"
        wrapped = _wrap_text(text, width=20)
        
        # Check that text is wrapped
        lines = wrapped.split('\n')
        for line in lines:
            assert len(line) <= 20


class TestFilters:
    """Test content filtering."""
    
    def test_content_filter_initialization(self):
        from socialai.config import Config
        from socialai.filters import ContentFilter
        
        config = Config.load()
        filter_obj = ContentFilter(config)
        
        assert filter_obj is not None
        assert isinstance(filter_obj.rules, list)
    
    def test_focus_mode_filter(self):
        from socialai.filters import FocusModeFilter
        
        filter_obj = FocusModeFilter(hide_engagement=True)
        
        content = "This is a post with 100 likes and 50 comments"
        filtered = filter_obj.filter_content(content)
        
        # Engagement metrics should be hidden
        assert "100 likes" not in filtered
        assert "50 comments" not in filtered


class TestPostModel:
    """Test Post data model."""
    
    def test_post_creation(self):
        from socialai.adapters.base import Post, EngagementMetrics
        
        post = Post(
            id="test_123",
            content="Test content",
            title="Test Title",
            author="test_author",
            platform="twitter",
            metrics=EngagementMetrics(likes=10, shares=5)
        )
        
        assert post.id == "test_123"
        assert post.content == "Test content"
        assert post.reading_time_minutes >= 1
    
    def test_post_reading_time(self):
        from socialai.adapters.base import Post, EngagementMetrics
        
        # Short content
        short_post = Post(
            id="short",
            content="Short content",
            author="test",
            platform="test"
        )
        assert short_post.reading_time_minutes == 1
        
        # Long content
        long_content = " ".join(["word"] * 500)
        long_post = Post(
            id="long",
            content=long_content,
            author="test",
            platform="test"
        )
        assert long_post.reading_time_minutes >= 2
    
    def test_post_total_engagement(self):
        from socialai.adapters.base import Post, EngagementMetrics
        
        post = Post(
            id="test",
            content="Test",
            author="test",
            platform="test",
            metrics=EngagementMetrics(likes=10, shares=5, comments=3)
        )
        
        assert post.total_engagement == 18


class TestEngagementScore:
    """Test engagement scoring."""
    
    def test_calculate_engagement_score(self):
        from socialai.adapters.base import BaseAdapter, Post, EngagementMetrics
        from socialai.config import Config
        
        config = Config.load()
        
        # Create a mock adapter to test scoring
        class MockAdapter(BaseAdapter):
            def __init__(self, cfg):
                super().__init__(cfg)
        
        adapter = MockAdapter(config)
        
        # High engagement
        high_metrics = EngagementMetrics(likes=1000, shares=100, comments=50)
        high_score = adapter._calculate_engagement_score(high_metrics)
        assert high_score >= 5.0
        
        # Low engagement
        low_metrics = EngagementMetrics(likes=5, shares=0, comments=0)
        low_score = adapter._calculate_engagement_score(low_metrics)
        assert low_score >= 0.0
        
        # No metrics
        none_score = adapter._calculate_engagement_score(None)
        assert none_score == 5.0


class TestSessionModel:
    """Test session management."""
    
    def test_session_creation(self):
        from socialai.core.session import Session
        
        session = Session(
            platforms=["twitter", "reddit"],
            duration=30,
            is_focus_mode=True
        )
        
        assert session.id is not None
        assert session.platforms == ["twitter", "reddit"]
        assert session.duration == 30
        assert session.is_focus_mode
        assert session.is_active
    
    def test_session_time_tracking(self):
        from socialai.core.session import Session
        
        session = Session(duration=30)
        session.start_time = datetime.now(timezone.utc)
        
        elapsed = session.get_elapsed_minutes()
        assert elapsed >= 0
        
        remaining = session.get_time_remaining()
        assert remaining <= 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
