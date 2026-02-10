"""
Configuration Management

Handles application configuration with YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, validator


class AIConfig(BaseModel):
    """AI configuration settings."""
    provider: str = Field(default="openai", description="AI provider (openai, anthropic, local)")
    model: str = Field(default="gpt-4", description="AI model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model creativity")
    max_tokens: int = Field(default=1000, gt=0, description="Max response tokens")


class PlatformConfig(BaseModel):
    """Platform-specific configuration."""
    enabled: bool = True
    hide_likes: bool = False
    hide_retweets: bool = False
    hide_comments: bool = False
    focus_mode: bool = False
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None


class TwitterConfig(PlatformConfig):
    """Twitter-specific configuration."""
    pass


class RedditConfig(PlatformConfig):
    """Reddit-specific configuration."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: Optional[str] = None


class LinkedInConfig(PlatformConfig):
    """LinkedIn-specific configuration."""
    pass


class FocusConfig(BaseModel):
    """Focus mode configuration."""
    enabled: bool = True
    session_duration: int = Field(default=30, gt=0, description="Session duration in minutes")
    break_interval: int = Field(default=5, gt=0, description="Break interval in minutes")
    content_filter: List[Dict[str, Any]] = Field(default_factory=list)


class OutputConfig(BaseModel):
    """Output configuration."""
    format: str = Field(default="rich", description="Output format (rich, json, plain)")
    color: bool = Field(default=True, description="Enable colored output")
    width: int = Field(default=80, gt=40, description="Output width")
    wrap_text: bool = Field(default=True, description="Wrap long text")


class StorageConfig(BaseModel):
    """Storage configuration."""
    db_path: str = Field(default="./data/socialai.db", description="Database path")
    cache_ttl: int = Field(default=3600, gt=0, description="Cache TTL in seconds")
    max_history: int = Field(default=1000, gt=0, description="Max history entries")


class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("SOCIALAI_CONFIG", "./config.yaml")
        self.data_dir = os.getenv("SOCIALAI_DATA_DIR", "./data")
        
        # Load configuration
        self._config = self._load_config()
        
        # Initialize sub-configs
        self.ai = AIConfig(**self._config.get("ai", {}))
        self.focus = FocusConfig(**self._config.get("focus", {}))
        self.output = OutputConfig(**self._config.get("output", {}))
        self.storage = StorageConfig(**self._config.get("storage", {}))
        
        # Initialize platform configs
        self.platforms = type('Platforms', (), {
            'twitter': TwitterConfig(**self._config.get("platforms", {}).get("twitter", {})),
            'reddit': RedditConfig(**self._config.get("platforms", {}).get("reddit", {})),
            'linkedin': LinkedInConfig(**self._config.get("platforms", {}).get("linkedin", {})),
            'hackernews': PlatformConfig(**self._config.get("platforms", {}).get("hackernews", {})),
        })()
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file."""
        return cls(config_path)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            # Create default configuration
            default_config = self._get_default_config()
            self._save_default_config(default_config)
            return default_config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"Failed to load config file {config_file}: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "ai": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "platforms": {
                "twitter": {
                    "enabled": True,
                    "hide_likes": True,
                    "hide_retweets": False,
                    "focus_mode": True
                },
                "reddit": {
                    "enabled": True,
                    "hide_upvotes": True,
                    "collapse_comments": True
                },
                "linkedin": {
                    "enabled": True,
                    "hide_reactions": True,
                    "hide_comments": True
                },
                "hackernews": {
                    "enabled": True,
                    "hide_upvotes": True
                }
            },
            "focus": {
                "enabled": True,
                "session_duration": 30,
                "break_interval": 5,
                "content_filter": [
                    {
                        "type": "keyword",
                        "action": "hide",
                        "value": "controversy"
                    }
                ]
            },
            "output": {
                "format": "rich",
                "color": True,
                "width": 80
            },
            "storage": {
                "db_path": "./data/socialai.db",
                "cache_ttl": 3600,
                "max_history": 1000
            }
        }
    
    def _save_default_config(self, config: Dict[str, Any]) -> None:
        """Save default configuration to file."""
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            # Don't fail if we can't save the config
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config()
    
    def set_value(self, key: str, value: str) -> None:
        """Set a configuration value from string, with type conversion."""
        current_value = self.get(key)
        
        # Type conversion based on current value
        if current_value is None:
            # Try to infer type
            if value.lower() in ('true', 'false'):
                converted_value = value.lower() == 'true'
            elif value.isdigit():
                converted_value = int(value)
            elif value.replace('.', '').isdigit() and '.' in value:
                converted_value = float(value)
            elif value.startswith('[') and value.endswith(']'):
                converted_value = [item.strip() for item in value[1:-1].split(',')]
            else:
                converted_value = value
        else:
            # Use the type of current value
            if isinstance(current_value, bool):
                converted_value = value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(current_value, int):
                converted_value = int(value)
            elif isinstance(current_value, float):
                converted_value = float(value)
            elif isinstance(current_value, list):
                converted_value = [item.strip() for item in value.split(',')]
            else:
                converted_value = value
        
        self.set(key, converted_value)
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save config file {self.config_path}: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service, checking environment first."""
        # Check environment variable
        env_key = f"{service.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        if api_key:
            return api_key
        
        # Check config
        return self.get(f"api_keys.{service}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate AI configuration
        if self.ai.provider not in ['openai', 'anthropic', 'local']:
            issues.append(f"Invalid AI provider: {self.ai.provider}")
        
        # Validate platform configurations
        for platform_name in ['twitter', 'reddit', 'linkedin']:
            platform_config = getattr(self.platforms, platform_name)
            if platform_config.enabled:
                # Check for required API keys
                if platform_name == 'reddit':
                    if not (platform_config.client_id or self.get_api_key('reddit')):
                        issues.append(f"Reddit API key not configured")
                elif platform_name == 'twitter':
                    # Twitter requires multiple credentials
                    has_creds = any([
                        self.get_api_key('twitter'),
                        getattr(platform_config, 'api_key', None),
                        getattr(platform_config, 'access_token', None)
                    ])
                    if not has_creds:
                        issues.append(f"Twitter credentials not configured")
        
        # Validate focus configuration
        if self.focus.session_duration <= 0:
            issues.append("Focus session duration must be positive")
        
        if self.focus.break_interval <= 0:
            issues.append("Focus break interval must be positive")
        
        # Validate output configuration
        if self.output.width < 40:
            issues.append("Output width must be at least 40 characters")
        
        return issues
    
    def __repr__(self) -> str:
        return f"Config(path='{self.config_path}')"


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance
