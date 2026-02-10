"""
Twitter/X Adapter

Adapter for Twitter/X API integration.
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

from socialai.config import Config
from socialai.adapters.base import BaseAdapter, Post, EngagementMetrics


class TwitterAdapter(BaseAdapter):
    """Twitter/X platform adapter."""
    
    platform_name = "twitter"
    supports_search = True
    supports_threads = True
    supports_direct_urls = True
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.api_key = config.get_api_key('twitter')
        self.base_url = "https://api.twitter.com/2"
        self.rate_limit_delay = 2.0
    
    async def fetch_feed(self, limit: int = 20, **kwargs) -> List[Post]:
        """Fetch user's Twitter feed (mock implementation)."""
        # Mock data for demonstration - in real implementation, use Twitter API
        mock_posts = []
        
        for i in range(min(limit, 5)):
            post = Post(
                id=f"mock_tweet_{i}",
                content=f"Mock tweet content {i}. This is a sample tweet for testing the SocialAI CLI tool. #demo #socialai",
                author=f"user_{i}",
                author_id=f"user_id_{i}",
                platform="twitter",
                url=f"https://twitter.com/user_{i}/status/mock_tweet_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    likes=i * 10,
                    retweets=i * 5,
                    comments=i * 2,
                    views=i * 100
                )
            )
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific Twitter post (mock implementation)."""
        # Mock post for demonstration
        post = Post(
            id=post_id,
            content="This is a mock tweet for demonstration purposes. In a real implementation, this would fetch the actual tweet using the Twitter API.",
            author="demo_user",
            author_id="demo_user_id",
            platform="twitter",
            url=f"https://twitter.com/demo_user/status/{post_id}",
            created_at=datetime.now(timezone.utc),
            metrics=EngagementMetrics(
                likes=42,
                retweets=12,
                comments=8,
                views=500
            )
        )
        
        post.engagement_score = self._calculate_engagement_score(post.metrics)
        post.tags = self._extract_tags(post.content)
        post.content = self._sanitize_content(post.content)
        
        return post
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Post]:
        """Search Twitter posts (mock implementation)."""
        mock_posts = []
        
        for i in range(min(limit, 3)):
            post = Post(
                id=f"search_result_{i}",
                content=f"Search result for '{query}': Mock tweet {i} containing relevant information about the search topic.",
                author=f"searcher_{i}",
                author_id=f"searcher_id_{i}",
                platform="twitter",
                url=f"https://twitter.com/searcher_{i}/status/search_result_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    likes=i * 8,
                    retweets=i * 3,
                    comments=i * 1,
                    views=i * 80
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    def _is_supported_url(self, url: str) -> bool:
        """Check if URL is a Twitter URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return domain in ['twitter.com', 'x.com']
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract tweet ID from Twitter URL."""
        patterns = [
            r'/status/(\d+)',
            r'/statuses/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _fetch_replies(self, post_id: str, max_replies: int) -> List[Post]:
        """Fetch replies to a tweet (mock implementation)."""
        replies = []
        
        for i in range(min(max_replies, 2)):
            reply = Post(
                id=f"reply_{post_id}_{i}",
                content=f"This is a mock reply {i} to the tweet {post_id}. Replies would be fetched using the Twitter API in a real implementation.",
                author=f"replier_{i}",
                author_id=f"replier_id_{i}",
                platform="twitter",
                url=f"https://twitter.com/replier_{i}/status/reply_{post_id}_{i}",
                created_at=datetime.now(timezone.utc),
                is_reply=True,
                reply_to_id=post_id,
                metrics=EngagementMetrics(
                    likes=i * 5,
                    comments=0,
                    views=i * 40
                )
            )
            
            reply.engagement_score = self._calculate_engagement_score(reply.metrics)
            reply.tags = self._extract_tags(reply.content)
            reply.content = self._sanitize_content(reply.content)
            replies.append(reply)
        
        return replies


# Reddit Adapter
class RedditAdapter(BaseAdapter):
    """Reddit platform adapter."""
    
    platform_name = "reddit"
    supports_search = True
    supports_threads = True
    supports_direct_urls = True
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.api_key = config.get_api_key('reddit')
        self.base_url = "https://www.reddit.com"
        self.rate_limit_delay = 1.0
    
    async def fetch_feed(self, limit: int = 20, **kwargs) -> List[Post]:
        """Fetch Reddit feed (mock implementation)."""
        mock_posts = []
        
        for i in range(min(limit, 5)):
            post = Post(
                id=f"reddit_post_{i}",
                content=f"Mock Reddit post content {i}. This would typically be a longer post with more detailed content. Perfect for AI summarization testing.",
                title=f"Interesting Reddit Post #{i}",
                author=f"reddit_user_{i}",
                author_id=f"redditor_{i}",
                platform="reddit",
                url=f"https://reddit.com/r/test/comments/post_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    upvotes=i * 15,
                    downvotes=i * 2,
                    comments=i * 8,
                    views=i * 200
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific Reddit post (mock implementation)."""
        post = Post(
            id=post_id,
            content="This is a mock Reddit post for demonstration. In reality, this would be fetched using the Reddit API and would contain the actual post content.",
            title=f"Demo Reddit Post {post_id}",
            author="demo_poster",
            author_id="redditor_demo",
            platform="reddit",
            url=f"https://reddit.com/r/demos/comments/{post_id}",
            created_at=datetime.now(timezone.utc),
            metrics=EngagementMetrics(
                upvotes=67,
                downvotes=12,
                comments=23,
                views=1000
            )
        )
        
        post.engagement_score = self._calculate_engagement_score(post.metrics)
        post.tags = self._extract_tags(post.content)
        post.content = self._sanitize_content(post.content)
        
        return post
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Post]:
        """Search Reddit posts (mock implementation)."""
        mock_posts = []
        
        for i in range(min(limit, 3)):
            post = Post(
                id=f"reddit_search_{i}",
                content=f"Search results for '{query}' on Reddit. Mock post {i} containing discussion about the topic.",
                title=f"Discussion about {query} - Part {i}",
                author=f"redditor_search_{i}",
                author_id=f"redditor_search_id_{i}",
                platform="reddit",
                url=f"https://reddit.com/r/search/comments/search_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    upvotes=i * 20,
                    comments=i * 6,
                    views=i * 150
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    def _is_supported_url(self, url: str) -> bool:
        """Check if URL is a Reddit URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return 'reddit.com' in domain
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract post ID from Reddit URL."""
        patterns = [
            r'/comments/([a-zA-Z0-9]+)',
            r'/r/\w+/comments/([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


# LinkedIn Adapter
class LinkedInAdapter(BaseAdapter):
    """LinkedIn platform adapter."""
    
    platform_name = "linkedin"
    supports_search = True
    supports_threads = False  # LinkedIn doesn't have traditional threads
    supports_direct_urls = True
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.api_key = config.get_api_key('linkedin')
        self.base_url = "https://api.linkedin.com"
        self.rate_limit_delay = 2.0
    
    async def fetch_feed(self, limit: int = 20, **kwargs) -> List[Post]:
        """Fetch LinkedIn feed (mock implementation)."""
        mock_posts = []
        
        professional_content = [
            "Just finished an amazing AI workshop! The future of technology is here. Excited to see how AI continues to transform our work.",
            "Sharing insights from our latest quarterly review. Our team's dedication to innovation continues to drive incredible results.",
            "Congratulations to the entire team on our successful product launch! This is what collaboration and hard work look like.",
            "Reflecting on the importance of continuous learning in today's fast-paced business environment. #ProfessionalGrowth",
            "Grateful for the opportunity to speak at the industry conference. The networking and knowledge sharing was invaluable."
        ]
        
        for i in range(min(limit, 5)):
            post = Post(
                id=f"linkedin_post_{i}",
                content=professional_content[i % len(professional_content)],
                author=f"Professional {i}",
                author_id=f"linkedin_user_{i}",
                platform="linkedin",
                url=f"https://linkedin.com/posts/user_{i}_post_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    likes=i * 25,
                    shares=i * 8,
                    comments=i * 4,
                    views=i * 300
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific LinkedIn post (mock implementation)."""
        post = Post(
            id=post_id,
            content="Professional LinkedIn post content for demonstration. This would contain career insights, industry updates, or company announcements in a real implementation.",
            author="Demo Professional",
            author_id="linkedin_demo_user",
            platform="linkedin",
            url=f"https://linkedin.com/posts/demo_post_{post_id}",
            created_at=datetime.now(timezone.utc),
            metrics=EngagementMetrics(
                likes=89,
                shares=15,
                comments=7,
                views=1200
            )
        )
        
        post.engagement_score = self._calculate_engagement_score(post.metrics)
        post.tags = self._extract_tags(post.content)
        post.content = self._sanitize_content(post.content)
        
        return post
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Post]:
        """Search LinkedIn posts (mock implementation)."""
        mock_posts = []
        
        search_content = [
            f"Professional insights about {query} that I wanted to share with my network.",
            f"Thoughtful discussion about {query} - what are your thoughts on this trend?",
            f"After years of experience with {query}, here are my key takeaways for the community."
        ]
        
        for i in range(min(limit, 3)):
            post = Post(
                id=f"linkedin_search_{i}",
                content=search_content[i % len(search_content)],
                author=f"Professional Search {i}",
                author_id=f"linkedin_search_user_{i}",
                platform="linkedin",
                url=f"https://linkedin.com/posts/search_user_{i}_search_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    likes=i * 30,
                    shares=i * 12,
                    comments=i * 6,
                    views=i * 400
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts


# Hacker News Adapter
class HackerNewsAdapter(BaseAdapter):
    """Hacker News adapter."""
    
    platform_name = "hackernews"
    supports_search = True
    supports_threads = True
    supports_direct_urls = True
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.rate_limit_delay = 1.0
    
    async def fetch_feed(self, limit: int = 20, **kwargs) -> List[Post]:
        """Fetch Hacker News top stories (mock implementation)."""
        tech_topics = [
            "AI breakthrough in natural language processing",
            "New JavaScript framework takes web development by storm",
            "Open source project reaches 100k GitHub stars",
            "Developer productivity tools that changed everything",
            "Why we need to rethink software architecture"
        ]
        
        mock_posts = []
        
        for i in range(min(limit, 5)):
            post = Post(
                id=f"hn_post_{i}",
                content=f"Hacker News story: {tech_topics[i % len(tech_topics)]}. This would typically link to an external article with a discussion thread.",
                title=tech_topics[i % len(tech_topics)],
                author=f"hacker_{i}",
                author_id=f"user_{i}",
                platform="hackernews",
                url=f"https://news.ycombinator.com/item?id=hn_post_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    upvotes=i * 40,
                    comments=i * 10,
                    views=i * 500
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific Hacker News post (mock implementation)."""
        post = Post(
            id=post_id,
            content="Hacker News post content about a technology topic. In reality, this would contain the actual story content and comments from the community.",
            title=f"Hacker News Story {post_id}",
            author="hn_user",
            author_id="demo_hn_user",
            platform="hackernews",
            url=f"https://news.ycombinator.com/item?id={post_id}",
            created_at=datetime.now(timezone.utc),
            metrics=EngagementMetrics(
                upvotes=156,
                comments=42,
                views=2500
            )
        )
        
        post.engagement_score = self._calculate_engagement_score(post.metrics)
        post.tags = self._extract_tags(post.content)
        post.content = self._sanitize_content(post.content)
        
        return post
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Post]:
        """Search Hacker News (mock implementation)."""
        mock_posts = []
        
        search_topics = [
            f"Discussion about {query} - What do you think?",
            f"My experience with {query} - Lessons learned",
            f"Why {query} matters for the future of tech"
        ]
        
        for i in range(min(limit, 3)):
            post = Post(
                id=f"hn_search_{i}",
                content=search_topics[i % len(search_topics)],
                title=search_topics[i % len(search_topics)],
                author=f"hn_searcher_{i}",
                author_id=f"user_search_{i}",
                platform="hackernews",
                url=f"https://news.ycombinator.com/item?id=hn_search_{i}",
                created_at=datetime.now(timezone.utc),
                metrics=EngagementMetrics(
                    upvotes=i * 35,
                    comments=i * 8,
                    views=i * 600
                )
            )
            
            post.engagement_score = self._calculate_engagement_score(post.metrics)
            post.tags = self._extract_tags(post.content)
            post.content = self._sanitize_content(post.content)
            mock_posts.append(post)
        
        return mock_posts
    
    def _is_supported_url(self, url: str) -> bool:
        """Check if URL is a Hacker News URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return 'news.ycombinator.com' in domain or 'hn.algolia.com' in domain
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract post ID from Hacker News URL."""
        pattern = r'/item\?id=(\d+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
