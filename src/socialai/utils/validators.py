"""
Input Validation Utilities

Validation functions for URLs, platforms, and other inputs.
"""

import re
import socket
import ipaddress
from typing import Optional, List
from urllib.parse import urlparse

# Set of known safe social media / content domains for the allowlist.
# URLs pointing to these domains are always permitted.
URL_ALLOWLIST = {
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "reddit.com", "www.reddit.com",
    "linkedin.com", "www.linkedin.com",
    "hackernews.com", "www.hackernews.com", "news.ycombinator.com",
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com",
    "youtube.com", "www.youtube.com",
    "github.com", "www.github.com",
    "medium.com", "www.medium.com",
    "dev.to", "www.dev.to",
}


def _is_private_hostname(hostname: str) -> bool:
    """Check if a hostname resolves to a private or internal IP address.

    Returns True for known loopback hosts, private IP ranges,
    link-local addresses, and unspecified addresses.
    """
    # Immediate string matches for common internal names
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1"):
        return True

    # Internal TLDs / unresolvable namespaces (RFC 6761, RFC 2606)
    if hostname.endswith(".local") or hostname.endswith(".internal"):
        return True

    # Try DNS resolution and inspect the resolved IP
    try:
        addr = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(addr)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_unspecified
            or ip_obj.is_multicast
        ):
            return True
    except (socket.gaierror, OSError, ValueError):
        # If we can't resolve, err on the side of caution — block it
        # to prevent DNS rebinding / SSRF to internal resolvers.
        return True

    return False


def validate_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL.

    Enforces SSRF protections:
      - Only http / https schemes are allowed.
      - Private, loopback, link-local, multicast, and unspecified IPs are blocked.
      - Hostnames that cannot be resolved are blocked (prevents DNS rebinding).

    Args:
        url: URL string to validate

    Returns:
        True if valid and safe URL, False otherwise
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False

        # Only allow http and https
        if result.scheme not in ("http", "https"):
            return False

        # Extract hostname (lowercased, without port)
        hostname = result.hostname
        if not hostname:
            return False

        # Allow-list check: if the hostname is a known safe domain, skip IP checks
        if hostname.lower() in URL_ALLOWLIST:
            return True

        # Block internal / private hosts
        if _is_private_hostname(hostname):
            return False

        return True
    except Exception:
        return False


def validate_platform(platform: str) -> bool:
    """
    Validate if platform is supported.
    
    Args:
        platform: Platform name to validate
    
    Returns:
        True if supported platform, False otherwise
    """
    supported_platforms = [
        'twitter', 'reddit', 'linkedin', 'hackernews', 
        'x', 'hn', 'facebook', 'instagram', 'tiktok'
    ]
    return platform.lower() in supported_platforms


def validate_ai_provider(provider: str) -> bool:
    """
    Validate AI provider.
    
    Args:
        provider: AI provider name
    
    Returns:
        True if supported provider, False otherwise
    """
    supported_providers = ['openai', 'anthropic', 'local', 'huggingface']
    return provider.lower() in supported_providers


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_positive_integer(value: str) -> bool:
    """
    Validate if string represents a positive integer.
    
    Args:
        value: String to validate
    
    Returns:
        True if positive integer, False otherwise
    """
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def validate_positive_float(value: str) -> bool:
    """
    Validate if string represents a positive float.
    
    Args:
        value: String to validate
    
    Returns:
        True if positive float, False otherwise
    """
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False


def validate_search_query(query: str, min_length: int = 2, max_length: int = 100) -> bool:
    """
    Validate search query.
    
    Args:
        query: Search query to validate
        min_length: Minimum length required
        max_length: Maximum length allowed
    
    Returns:
        True if valid query, False otherwise
    """
    if not query or not isinstance(query, str):
        return False
    
    query = query.strip()
    return min_length <= len(query) <= max_length


def validate_content_filter(filter_type: str, value: str) -> bool:
    """
    Validate content filter configuration.
    
    Args:
        filter_type: Type of filter (keyword, sentiment, etc.)
        value: Filter value
    
    Returns:
        True if valid filter, False otherwise
    """
    valid_filter_types = ['keyword', 'sentiment', 'topic', 'author', 'platform']
    
    if filter_type not in valid_filter_types:
        return False
    
    # Basic validation for filter value
    if not value or not isinstance(value, str):
        return False
    
    return True


def validate_session_duration(duration: int) -> bool:
    """
    Validate session duration.
    
    Args:
        duration: Duration in minutes
    
    Returns:
        True if valid duration, False otherwise
    """
    return 5 <= duration <= 480  # Between 5 minutes and 8 hours


def validate_output_format(format_type: str) -> bool:
    """
    Validate output format.
    
    Args:
        format_type: Output format type
    
    Returns:
        True if supported format, False otherwise
    """
    supported_formats = ['rich', 'json', 'plain', 'markdown', 'csv']
    return format_type.lower() in supported_formats


def validate_platform_list(platforms: List[str]) -> List[str]:
    """
    Validate and filter platform list.
    
    Args:
        platforms: List of platform names
    
    Returns:
        List of valid platform names
    """
    if not platforms:
        return []
    
    valid_platforms = []
    for platform in platforms:
        if validate_platform(platform):
            valid_platforms.append(platform.lower())
    
    return list(set(valid_platforms))  # Remove duplicates


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Filename to sanitize
    
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_filename = re.sub(r'\s+', '_', safe_filename)  # Replace spaces with underscore
    safe_filename = safe_filename.strip('_')  # Remove leading/trailing underscores
    
    # Limit length
    if len(safe_filename) > 100:
        safe_filename = safe_filename[:100]
    
    return safe_filename or "unnamed_file"


def validate_url_pattern(url: str, patterns: List[str]) -> bool:
    """
    Check if URL matches any of the given patterns.
    
    Args:
        url: URL to check
        patterns: List of URL patterns (supports wildcards)
    
    Returns:
        True if URL matches any pattern
    """
    for pattern in patterns:
        # Convert pattern to regex
        regex_pattern = pattern.replace('*', '.*')
        regex_pattern = f'^{regex_pattern}$'
        
        if re.match(regex_pattern, url, re.IGNORECASE):
            return True
    
    return False
