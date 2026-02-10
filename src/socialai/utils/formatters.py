"""
Content Formatting

Utilities for formatting posts and summaries for display.
"""

import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.columns import Columns
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def format_post(post: 'Post', minimal: bool = False, max_width: int = 80) -> str:
    """
    Format a post for display.
    
    Args:
        post: Post object to format
        minimal: Whether to use minimal formatting (for focus mode)
        max_width: Maximum width for text wrapping
    
    Returns:
        Formatted post as string
    """
    if not RICH_AVAILABLE or not minimal:
        return _format_post_text(post, minimal, max_width)
    else:
        return _format_post_rich(post, minimal, max_width)


def _format_post_text(post: 'Post', minimal: bool = False, max_width: int = 80) -> str:
    """Format post using plain text."""
    lines = []
    
    if not minimal:
        # Title
        if post.title:
            lines.append(f"Title: {post.title}")
        else:
            lines.append(f"Content: {post.content[:100]}{'...' if len(post.content) > 100 else ''}")
        
        # Author and platform
        lines.append(f"Author: {post.author} | Platform: {post.platform.title()}")
        
        # Engagement
        if post.metrics:
            metrics = []
            if post.metrics.likes:
                metrics.append(f"👍 {post.metrics.likes}")
            if post.metrics.comments:
                metrics.append(f"💬 {post.metrics.comments}")
            if post.metrics.shares:
                metrics.append(f"🔄 {post.metrics.shares}")
            if post.metrics.upvotes:
                metrics.append(f"⬆️ {post.metrics.upvotes}")
            if post.metrics.retweets:
                metrics.append(f"🔁 {post.metrics.retweets}")
            if metrics:
                lines.append(" | ".join(metrics))
        
        # Tags
        if post.tags:
            lines.append(f"Tags: {', '.join(post.tags)}")
        
        # Score
        if post.engagement_score:
            lines.append(f"Score: {post.engagement_score:.1f}/10")
        
        lines.append("-" * 60)
    
    # Content
    content = post.content
    if minimal:
        # Truncate for minimal mode
        if len(content) > max_width * 2:
            content = content[:max_width * 2 - 3] + "..."
    
    # Wrap text
    wrapped_content = _wrap_text(content, max_width)
    lines.append(wrapped_content)
    
    # Summary (if available and not minimal)
    if post.summary and not minimal:
        lines.append("\n[AI Summary]")
        lines.append(_wrap_text(post.summary, max_width))
    
    # Key topics
    if post.key_topics and not minimal:
        lines.append(f"\nKey Topics: {', '.join(post.key_topics)}")
    
    return "\n".join(lines)


def _format_post_rich(post: 'Post', minimal: bool = False, max_width: int = 80) -> str:
    """Format post using Rich formatting (returns rich text)."""
    console = Console()
    
    # Create content
    content_parts = []
    
    if not minimal:
        # Header with title and metadata
        if post.title:
            content_parts.append(f"[bold blue]{post.title}[/bold blue]")
        else:
            # Truncate content for title
            title_content = post.content[:50] + "..." if len(post.content) > 50 else post.content
            content_parts.append(f"[bold blue]{title_content}[/bold blue]")
        
        # Metadata
        metadata = f"[dim]By: {post.author} | Platform: {post.platform.title()}"
        if post.created_at:
            created = post.created_at.strftime("%Y-%m-%d %H:%M")
            metadata += f" | {created}"
        
        content_parts.append(metadata)
        
        # Engagement metrics
        if post.metrics:
            metrics = []
            if post.metrics.likes:
                metrics.append(f"👍 {post.metrics.likes}")
            if post.metrics.comments:
                metrics.append(f"💬 {post.metrics.comments}")
            if post.metrics.upvotes:
                metrics.append(f"⬆️ {post.metrics.upvotes}")
            if post.engagement_score:
                metrics.append(f"⭐ {post.engagement_score:.1f}/10")
            
            if metrics:
                content_parts.append(f"[green]{' | '.join(metrics)}[/green]")
        
        # Tags
        if post.tags:
            tags_text = " ".join(f"[cyan]{tag}[/cyan]" for tag in post.tags[:5])  # Limit to 5 tags
            content_parts.append(f"Tags: {tags_text}")
        
        content_parts.append("")  # Empty line
    
    # Main content
    content = post.content
    if minimal and len(content) > max_width * 2:
        content = content[:max_width * 2 - 3] + "..."
    
    # Remove Rich markup for plain text output
    clean_content = re.sub(r'\[.*?\]', '', content)
    content_parts.append(clean_content)
    
    # AI summary (if available and not minimal)
    if post.summary and not minimal:
        content_parts.append("")
        content_parts.append("[yellow][AI Summary][/yellow]")
        summary_clean = re.sub(r'\[.*?\]', '', post.summary)
        content_parts.append(summary_clean)
    
    # Key topics
    if post.key_topics and not minimal:
        content_parts.append("")
        topics_text = " ".join(f"[cyan]{topic}[/cyan]" for topic in post.key_topics[:3])
        content_parts.append(f"Key Topics: {topics_text}")
    
    return "\n".join(content_parts)


def format_summary(summary: str) -> str:
    """Format AI summary for display."""
    if not RICH_AVAILABLE:
        # Plain text formatting
        return f"\n[AI Summary]\n{summary}"
    
    # Rich formatting
    clean_summary = re.sub(r'\[.*?\]', '', summary)  # Remove existing markup
    return clean_summary


def format_search_results(results: Dict[str, List['Post']], query: str) -> str:
    """Format search results from multiple platforms."""
    if not RICH_AVAILABLE:
        return _format_search_results_text(results, query)
    else:
        return _format_search_results_rich(results, query)


def _format_search_results_text(results: Dict[str, List['Post']], query: str) -> str:
    """Format search results as plain text."""
    lines = []
    lines.append(f"Search Results for: '{query}'")
    lines.append("=" * 60)
    
    for platform, posts in results.items():
        lines.append(f"\n[ {platform.upper()} ]")
        lines.append("-" * 40)
        
        for i, post in enumerate(posts, 1):
            lines.append(f"{i}. {post.title or post.content[:80]}...")
            lines.append(f"   By: {post.author} | Score: {post.engagement_score or 'N/A'}")
            if post.metrics:
                metrics = []
                if post.metrics.likes:
                    metrics.append(f"👍{post.metrics.likes}")
                if post.metrics.comments:
                    metrics.append(f"💬{post.metrics.comments}")
                if metrics:
                    lines.append(f"   {' '.join(metrics)}")
    
    return "\n".join(lines)


def _format_search_results_rich(results: Dict[str, List['Post']], query: str) -> str:
    """Format search results using Rich."""
    lines = []
    lines.append(f"[bold]Search Results for: '{query}'[/bold]")
    lines.append("")
    
    for platform, posts in results.items():
        lines.append(f"[bold cyan][ {platform.upper()} ][/bold cyan]")
        lines.append("")
        
        for i, post in enumerate(posts, 1):
            # Post title
            title = post.title or post.content[:60] + "..." if len(post.content) > 60 else post.content
            lines.append(f"[bold white]{i}. {title}[/bold white]")
            
            # Metadata
            metadata = f"[dim]By: {post.author}"
            if post.engagement_score:
                metadata += f" | Score: {post.engagement_score:.1f}"
            lines.append(metadata)
            
            # Engagement
            if post.metrics:
                metrics = []
                if post.metrics.likes:
                    metrics.append(f"👍 {post.metrics.likes}")
                if post.metrics.comments:
                    metrics.append(f"💬 {post.metrics.comments}")
                if metrics:
                    lines.append(f"[green]{'  '.join(metrics)}[/green]")
            
            lines.append("")
    
    return "\n".join(lines)


def _wrap_text(text: str, width: int) -> str:
    """Wrap text to specified width."""
    lines = []
    words = text.split()
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        
        # Check if adding this word would exceed width
        if current_length + word_length + (1 if current_line else 0) > width:
            # Start new line
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length
        else:
            # Add to current line
            if current_line:
                current_line.append(word)
                current_length += word_length + 1
            else:
                current_line.append(word)
                current_length = word_length
    
    # Add final line
    if current_line:
        lines.append(" ".join(current_line))
    
    return "\n".join(lines)


def format_engagement_score(score: float) -> str:
    """Format engagement score with appropriate color/emoji."""
    if not RICH_AVAILABLE:
        if score >= 8:
            return "🔥 High (8-10)"
        elif score >= 6:
            return "📈 Medium (6-7.9)"
        elif score >= 4:
            return "📊 Average (4-5.9)"
        else:
            return "📉 Low (0-3.9)"
    
    # Rich formatting
    if score >= 8:
        return f"[bold green]🔥 High ({score:.1f}/10)[/bold green]"
    elif score >= 6:
        return f"[green]📈 Medium ({score:.1f}/10)[/green]"
    elif score >= 4:
        return f"[yellow]📊 Average ({score:.1f}/10)[/yellow]"
    else:
        return f"[red]📉 Low ({score:.1f}/10)[/red]"


def format_timestamp(dt: Optional[datetime]) -> str:
    """Format timestamp for display."""
    if not dt:
        return "Unknown"
    
    now = datetime.now(dt.tzinfo)
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


# Forward reference
from socialai.adapters.base import Post
