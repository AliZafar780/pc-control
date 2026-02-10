"""
AI Service Module

Provides AI-powered summarization, analysis, and insights.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from pydantic import BaseModel

# AI provider imports (optional - handled gracefully)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class ContentSummary:
    """Structured summary of content."""
    brief: str
    detailed: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    key_topics: Optional[List[str]] = None
    sentiment: Optional[str] = None
    reading_time_minutes: Optional[int] = None


@dataclass
class EngagementScore:
    """Content engagement scoring result."""
    score: float  # 0-10
    analysis: str
    factors: Dict[str, float]
    recommendation: str


@dataclass
class Insight:
    """AI-generated insight."""
    category: str
    text: str
    confidence: float
    sources: List[str]


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def summarize(self, content: str, style: str = "brief") -> str:
        """Generate a summary of content."""
        pass
    
    @abstractmethod
    async def score_content(self, content: str) -> EngagementScore:
        """Score content for engagement potential."""
        pass
    
    @abstractmethod
    async def extract_insights(self, query: str, context: Optional[str] = None) -> List[Insight]:
        """Extract key insights from content."""
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response to a prompt."""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, config: 'Config', model: str = "gpt-4"):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.config = config
        self.model = model
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", config.openai_api_key)
        )
    
    async def summarize(self, content: str, style: str = "brief") -> str:
        """Generate summary using OpenAI."""
        style_prompts = {
            "brief": "Provide a concise 2-3 sentence summary.",
            "detailed": "Provide a comprehensive summary with all key points.",
            "bullet": "Provide key points as a bulleted list."
        }
        
        prompt = f"""Summarize the following content. {style_prompts.get(style, style_prompts['brief'])}

Content:
{content}

Summary:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.ai.temperature,
            max_tokens=self.config.ai.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def score_content(self, content: str) -> EngagementScore:
        """Score content using OpenAI."""
        prompt = f"""Analyze this content and provide an engagement score from 0-10.
Consider factors like: relevance, emotional impact, uniqueness, and practical value.

Content:
{content[:1000]}

Provide your response as JSON with these fields:
- score (number 0-10)
- analysis (string explanation)
- factors (dict with scores for: relevance, emotion, uniqueness, value)
- recommendation (string with advice)

Respond only with valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        return EngagementScore(
            score=result.get("score", 5.0),
            analysis=result.get("analysis", ""),
            factors=result.get("factors", {}),
            recommendation=result.get("recommendation", "")
        )
    
    async def extract_insights(self, query: str, context: Optional[str] = None) -> List[Insight]:
        """Extract insights using OpenAI."""
        prompt = f"""Extract key insights from the following content.

Context: {context or 'General content analysis'}
Query: {query}

Provide insights as JSON array with objects containing:
- category (string)
- text (string)
- confidence (number 0-1)
- sources (array of source references)

Respond only with valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        insights = []
        for item in result.get("insights", []):
            insights.append(Insight(
                category=item.get("category", "general"),
                text=item.get("text", ""),
                confidence=item.get("confidence", 0.5),
                sources=item.get("sources", [])
            ))
        
        return insights
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.config.ai.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.ai.max_tokens)
        )
        
        return response.choices[0].message.content


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, config: 'Config', model: str = "claude-3-opus-20240229"):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.config = config
        self.model = model
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", config.anthropic_api_key)
        )
    
    async def summarize(self, content: str, style: str = "brief") -> str:
        """Generate summary using Anthropic."""
        style_instructions = {
            "brief": "Provide a concise 2-3 sentence summary.",
            "detailed": "Provide a comprehensive summary with all key points.",
            "bullet": "Provide key points as a bulleted list."
        }
        
        prompt = f"""\n\nHuman: Summarize the following content. {style_instructions.get(style, style_instructions['brief'])}

Content:
{content}

Summary:"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.config.ai.max_tokens,
            temperature=self.config.ai.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def score_content(self, content: str) -> EngagementScore:
        """Score content using Anthropic."""
        prompt = f"""\n\nHuman: Analyze this content and provide an engagement score from 0-10.
Consider factors like: relevance, emotional impact, uniqueness, and practical value.

Content:
{content[:1000]}

Provide your response as JSON with these fields:
- score (number 0-10)
- analysis (string explanation)
- factors (dict with scores for: relevance, emotion, uniqueness, value)
- recommendation (string with advice)

Respond only with valid JSON."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        result = json.loads(response.content[0].text)
        
        return EngagementScore(
            score=result.get("score", 5.0),
            analysis=result.get("analysis", ""),
            factors=result.get("factors", {}),
            recommendation=result.get("recommendation", "")
        )
    
    async def extract_insights(self, query: str, context: Optional[str] = None) -> List[Insight]:
        """Extract insights using Anthropic."""
        prompt = f"""\n\nHuman: Extract key insights from the following content.

Context: {context or 'General content analysis'}
Query: {query}

Provide insights as JSON array with objects containing:
- category (string)
- text (string)
- confidence (number 0-1)
- sources (array of source references)

Respond only with valid JSON."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        result = json.loads(response.content[0].text)
        
        insights = []
        for item in result.get("insights", []):
            insights.append(Insight(
                category=item.get("category", "general"),
                text=item.get("text", ""),
                confidence=item.get("confidence", 0.5),
                sources=item.get("sources", [])
            ))
        
        return insights
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.config.ai.max_tokens),
            temperature=kwargs.get("temperature", self.config.ai.temperature),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text


class LocalProvider(BaseAIProvider):
    """Local transformer model provider."""
    
    def __init__(self, config: 'Config', model_name: str = "facebook/bart-large-cnn"):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers package not installed. Run: pip install transformers torch")
        
        self.config = config
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.summarizer = pipeline("summarization", model=model_name, tokenizer=model_name)
    
    async def summarize(self, content: str, style: str = "brief") -> str:
        """Generate summary using local model."""
        max_length = 150 if style == "brief" else 300
        
        # Handle long content
        if len(content) > 2000:
            content = content[:2000]
        
        result = self.summarizer(
            content,
            max_length=max_length,
            min_length=30,
            do_sample=False
        )
        
        return result[0]['summary_text']
    
    async def score_content(self, content: str) -> EngagementScore:
        """Score content using local analysis."""
        # Simple heuristic-based scoring for local mode
        words = content.split()
        
        # Calculate basic metrics
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        # Score based on content quality indicators
        score = 5.0
        factors = {
            "relevance": 0.5,
            "emotion": 0.5,
            "uniqueness": 0.5,
            "value": 0.5
        }
        
        # Adjust based on content characteristics
        if avg_word_length > 5:
            factors["value"] = 0.7
            score += 0.5
        
        if len(words) > 50:
            factors["relevance"] = 0.6
            score += 0.3
        
        return EngagementScore(
            score=min(score, 10.0),
            analysis="Content analyzed using local model.",
            factors=factors,
            recommendation="Review content for engagement potential."
        )
    
    async def extract_insights(self, query: str, context: Optional[str] = None) -> List[Insight]:
        """Extract insights using local model."""
        # Simple extraction for local mode
        content = context or query
        words = content.split()
        
        insights = [
            Insight(
                category="summary",
                text=f"Content contains {len(words)} words.",
                confidence=0.8,
                sources=["local_analysis"]
            ),
            Insight(
                category="structure",
                text="Content appears to be well-structured text.",
                confidence=0.6,
                sources=["local_analysis"]
            )
        ]
        
        return insights
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using local model."""
        # For local models, return a simple acknowledgment
        return "Local model processing complete. For more advanced generation, please use OpenAI or Anthropic."


class AIService:
    """Main AI service that routes to appropriate provider."""
    
    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "local": LocalProvider,
    }
    
    def __init__(self, config: 'Config', provider: Optional[str] = None):
        self.config = config
        self.provider_name = provider or config.ai.provider
        self._provider = None
    
    @property
    def provider(self) -> BaseAIProvider:
        """Lazy load the AI provider."""
        if self._provider is None:
            provider_class = self.PROVIDERS.get(self.provider_name.lower())
            if not provider_class:
                raise ValueError(f"Unknown provider: {self.provider_name}")
            
            self._provider = provider_class(self.config)
        
        return self._provider
    
    async def summarize(self, content: str, style: str = "brief") -> str:
        """Generate a summary of content."""
        return await self.provider.summarize(content, style)
    
    async def score_content(self, content: str) -> EngagementScore:
        """Score content for engagement potential."""
        return await self.provider.score_content(content)
    
    async def extract_insights(self, query: str, context: Optional[str] = None) -> List[Insight]:
        """Extract key insights from content."""
        return await self.provider.extract_insights(query, context)
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response to a prompt."""
        return await self.provider.generate_response(prompt, **kwargs)


# Forward reference for type hint
from socialai.config import Config
