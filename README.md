# SocialAI - Distraction-Free AI-Powered Social Media CLI

A modern, distraction-free CLI tool for consuming social media content with AI-powered summarization, content filtering, and focus modes. Built with love for productivity enthusiasts.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

## Features

### 🤖 AI-Powered Intelligence
- **Smart Summarization**: Get AI-generated summaries of long posts and threads
- **Content Analysis**: Score content relevance with AI-powered engagement scoring
- **Quick Insights**: Extract key points from discussions without reading everything
- **Multiple Providers**: Support for OpenAI, Anthropic, and local models

### 🎯 Distraction-Free Design
- **Focus Mode**: Strip away likes, comments, and distractions
- **Content Filtering**: Filter by keywords, topics, or sentiment
- **Reading Time Estimates**: Know how long content will take to read
- **Minimal Interface**: Clean, terminal-first experience

### 📱 Multi-Platform Support
- **Twitter/X**: Read threads and tweets without engagement pollution
- **Reddit**: Browse subreddits with AI summarization
- **LinkedIn**: Professional content without distractions
- **Hacker News**: Tech news with smart ranking
- **Custom Adapters**: Easy to extend for more platforms

### ⚡ Productivity Features
- **Batch Processing**: Process multiple posts at once
- **Save for Later**: Bookmark content for focused reading
- **Export Options**: Save summaries to files
- **Session History**: Track your reading sessions

## Installation

### Quick Start
```bash
# Clone the repository
git clone https://github.com/AliZafar780/pc-control.git
cd pc-control

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Run the CLI
python -m socialai --help
```

### Environment Variables
```bash
# OpenAI (for GPT models)
export OPENAI_API_KEY="your-api-key"

# Anthropic (for Claude models)
export ANTHROPIC_API_KEY="your-api-key"

# Or use config file
export SOCIALAI_CONFIG="/path/to/config.yaml"
```

## Usage

### Basic Commands

```bash
# View your feed from a platform
socialai feed twitter --limit 20

# Summarize a thread
socialai summarize https://twitter.com/user/status/123456789

# Search content across platforms
socialai search "AI news" --platforms twitter reddit

# Enable focus mode
socialai focus --enable

# View saved items
socialai saved --list

# Run a focused session
socialai session start --platforms twitter reddit --duration 30
```

### AI Commands

```bash
# Get AI summary of content
socialai ai summarize --url "https://..."

# Analyze engagement potential
socialai ai score --content "content text"

# Extract key insights
socialai ai insights --query "what are the main points"

# Generate reading list
socialai ai recommendations --topics AI productivity
```

### Configuration

```bash
# Set default platform
socialai config set default_platform twitter

# Configure AI provider
socialai config set ai_provider openai

# Set focus mode preferences
socialai config set focus_mode true
socialai config set hide_likes true
socialai config set hide_comments true

# View current configuration
socialai config show
```

## Architecture

```
socialai/
 src/
   └── socialai/
       ├── __init__.py
       ├── cli.py              # CLI interface
       ├── main.py             # Entry point
       ├── ai.py               # AI integration
       ├── config.py           # Configuration
       ├── filters.py          # Content filters
       ├── adapters/           # Platform adapters
       │   ├── __init__.py
       │   ├── base.py         # Base adapter
       │   ├── twitter.py      # Twitter/X
       │   ├── reddit.py       # Reddit
       │   ├── linkedin.py      # LinkedIn
       │   └── hackernews.py    # Hacker News
       ├── core/               # Core functionality
       │   ├── __init__.py
       │   ├── feed.py         # Feed management
       │   ├── session.py      # Session management
       │   └── storage.py      # Data persistence
       └── utils/              # Utilities
           ├── __init__.py
           ├── formatters.py   # Output formatting
           └── validators.py   # Input validation
 tests/                     # Test suite
 docs/                      # Documentation
 config.example.yaml        # Example configuration
 requirements.txt           # Python dependencies
 setup.py                   # Package setup
 README.md                  # This file
```

## Configuration File

Create a `config.yaml` file:

```yaml
ai:
  provider: openai             # openai, anthropic, local
  model: gpt-4                # Model to use
  temperature: 0.7             # Creativity level
  max_tokens: 1000             # Max response length

platforms:
  twitter:
    enabled: true
    hide_likes: true
    hide_retweets: false
    focus_mode: true
  reddit:
    enabled: true
    hide_upvotes: true
    collapse_comments: true
  linkedin:
    enabled: true
    hide_reactions: true
    hide_comments: true

focus:
  enabled: true
  session_duration: 30         # minutes
  break_interval: 5            # minutes
  content_filter:
    - type: keyword
      action: hide
      value: controversy

output:
  format: rich                 # rich, json, plain
  color: true
  width: 80

storage:
  db_path: ./data/socialai.db
  cache_ttl: 3600              # seconds
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI models |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude models |
| `SOCIALAI_CONFIG` | Path to config file | Optional |
| `SOCIALAI_DATA_DIR` | Path to data directory | Optional |

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_adapters.py

# Run with coverage
pytest --cov=src/socialai
```

### Adding New Adapters
```python
from socialai.adapters.base import BaseAdapter

class MyPlatformAdapter(BaseAdapter):
    platform_name = "myplatform"
    
    async def fetch_feed(self, limit=20):
        # Implement feed fetching
        pass
    
    async def get_post(self, post_id):
        # Implement post fetching
        pass
    
    async def summarize_content(self, content):
        # Implement AI summarization
        pass
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

- 📧 Email: support@socialai.dev
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

Built with ❤️ for productivity enthusiasts who want to stay informed without the distraction.
