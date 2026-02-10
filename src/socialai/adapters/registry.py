"""
Adapter Registry

Manages registration and retrieval of platform adapters.
"""

from typing import Dict, List, Optional, Type
from urllib.parse import urlparse

from socialai.config import Config
from socialai.adapters.base import BaseAdapter


class AdapterRegistry:
    """
    Registry for managing platform adapters.
    
    Allows registration, retrieval, and discovery of platform-specific adapters.
    """
    
    def __init__(self, config: Config):
        """Initialize the registry with configuration."""
        self.config = config
        self._adapters: Dict[str, Type[BaseAdapter]] = {}
        self._adapter_instances: Dict[str, BaseAdapter] = {}
        
        # Auto-register built-in adapters
        self._register_builtin_adapters()
    
    def _register_builtin_adapters(self) -> None:
        """Register all built-in adapters."""
        from socialai.adapters.twitter import TwitterAdapter
        from socialai.adapters.reddit import RedditAdapter
        from socialai.adapters.linkedin import LinkedInAdapter
        from socialai.adapters.hackernews import HackerNewsAdapter
        
        self.register('twitter', TwitterAdapter)
        self.register('reddit', RedditAdapter)
        self.register('linkedin', LinkedInAdapter)
        self.register('hackernews', HackerNewsAdapter)
    
    def register(self, name: str, adapter_class: Type[BaseAdapter]) -> None:
        """
        Register a new adapter.
        
        Args:
            name: Platform name (e.g., 'twitter', 'reddit')
            adapter_class: Adapter class to register
        """
        self._adapters[name.lower()] = adapter_class
    
    def get_adapter(self, name: str) -> BaseAdapter:
        """
        Get an adapter instance by name.
        
        Args:
            name: Platform name
        
        Returns:
            Adapter instance
        
        Raises:
            ValueError: If adapter not found or platform disabled
        """
        name = name.lower()
        
        # Check if adapter is enabled in config
        platform_config = getattr(self.config.platforms, name, None)
        if platform_config and not platform_config.enabled:
            raise ValueError(f"Platform '{name}' is disabled in configuration")
        
        # Get or create adapter instance
        if name not in self._adapter_instances:
            if name not in self._adapters:
                raise ValueError(f"Adapter '{name}' not found")
            
            adapter_class = self._adapters[name]
            self._adapter_instances[name] = adapter_class(self.config)
        
        return self._adapter_instances[name]
    
    def get_adapter_for_url(self, url: str) -> Optional[BaseAdapter]:
        """
        Get the appropriate adapter for a given URL.
        
        Args:
            url: Full URL to analyze
        
        Returns:
            Adapter instance or None if no adapter matches
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Map domains to adapter names
        domain_mapping = {
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'reddit.com': 'reddit',
            'www.reddit.com': 'reddit',
            'linkedin.com': 'linkedin',
            'www.linkedin.com': 'linkedin',
            'news.ycombinator.com': 'hackernews',
            'hn.algolia.com': 'hackernews',
        }
        
        adapter_name = domain_mapping.get(domain)
        if not adapter_name:
            return None
        
        try:
            return self.get_adapter(adapter_name)
        except ValueError:
            return None
    
    def list_adapters(self) -> List[str]:
        """
        List all registered adapter names.
        
        Returns:
            List of adapter names
        """
        return list(self._adapters.keys())
    
    def list_enabled_adapters(self) -> List[str]:
        """
        List all enabled adapters based on configuration.
        
        Returns:
            List of enabled adapter names
        """
        enabled = []
        
        for name in self._adapters.keys():
            platform_config = getattr(self.config.platforms, name, None)
            if platform_config and platform_config.enabled:
                enabled.append(name)
        
        return enabled
    
    async def extract_content(self, url: str) -> Optional[Dict[str, any]]:
        """
        Extract content from a URL using the appropriate adapter.
        
        Args:
            url: URL to extract content from
        
        Returns:
            Extracted content dictionary or None
        """
        adapter = self.get_adapter_for_url(url)
        
        if not adapter:
            return None
        
        try:
            post = await adapter.extract_content_from_url(url)
            if post:
                return {
                    'url': url,
                    'platform': adapter.platform_name,
                    'content': post.content,
                    'title': post.title,
                    'author': post.author,
                    'post': post
                }
        except Exception:
            pass
        
        return None
    
    async def search_all(self, query: str, platforms: Optional[List[str]] = None) -> Dict[str, List]:
        """
        Search across multiple platforms.
        
        Args:
            query: Search query
            platforms: Optional list of platforms to search (all if None)
        
        Returns:
            Dictionary mapping platform names to lists of posts
        """
        results = {}
        
        # Determine which platforms to search
        if platforms:
            search_platforms = [p.lower() for p in platforms]
        else:
            search_platforms = self.list_enabled_adapters()
        
        # Search each platform
        for name in search_platforms:
            try:
                adapter = self.get_adapter(name)
                if adapter.supports_search:
                    posts = await adapter.search(query)
                    results[name] = posts
            except (ValueError, Exception):
                continue
        
        return results
    
    async def fetch_all_feeds(self, limit: int = 20) -> Dict[str, List]:
        """
        Fetch feeds from all enabled platforms.
        
        Args:
            limit: Number of posts per platform
        
        Returns:
            Dictionary mapping platform names to lists of posts
        """
        results = {}
        
        for name in self.list_enabled_adapters():
            try:
                adapter = self.get_adapter(name)
                posts = await adapter.fetch_feed(limit=limit)
                results[name] = posts
            except (ValueError, Exception):
                continue
        
        return results
