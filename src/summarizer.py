"""AI Article Summarizer module.

Generates summaries for articles using Google Gemini API.
Extracts article content from URLs and summarizes with AI.
"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse
import re

import requests

from src.config import get_env_var


# ============================================
# Configuration
# ============================================

# Content extraction endpoints (free options)
READABILITY_API = "https://r.jina.ai"  # jina.ai - free, no API key needed
MERCURY_API = "https://mercury.postlight.com/parser"  # requires API key

# Gemini API endpoint
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Request timeout (seconds)
REQUEST_TIMEOUT = 30


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment."""
    return get_env_var("GEMINI_API_KEY", required=False) or ""


def get_gemini_model() -> str:
    """Get Gemini model name from environment (default: gemini-2.0-flash-exp)."""
    return get_env_var("GEMINI_MODEL", required=False) or "gemini-2.0-flash-exp"


# ============================================
# Content Extraction
# ============================================

def extract_content_jina(url: str) -> Optional[str]:
    """Extract article content using jina.ai reader API (free, no API key).

    Args:
        url: Article URL to extract content from

    Returns:
        Extracted text content or None if failed
    """
    api_url = f"{READABILITY_API}/{url}"

    try:
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            content = response.text
            # Limit content length for API
            if len(content) > 15000:
                content = content[:15000]
            return content
        else:
            print(f"Jina API returned status {response.status_code} for {url}")
            return None
    except Exception as e:
        print(f"Error extracting content with Jina: {e}")
        return None


def extract_article_content(url: str) -> Optional[str]:
    """Extract article content from URL using available services.

    Args:
        url: Article URL to extract content from

    Returns:
        Extracted text content or None if all methods failed
    """
    # Try jina.ai first (free, reliable)
    content = extract_content_jina(url)

    if content:
        print(f"Successfully extracted content from {url} ({len(content)} chars)")
        return content

    print(f"Failed to extract content from {url}")
    return None


# ============================================
# AI Summarization
# ============================================

def build_summary_prompt(title: str, content: str) -> str:
    """Build prompt for Gemini API.

    Args:
        title: Article title
        content: Article content

    Returns:
        Formatted prompt string
    """
    return f"""You are a professional article summarizer. Your task is to create a concise, informative summary.

Article Title: {title}

Article Content:
{content}

Requirements:
1. Write in Korean (unless the content is clearly in English)
2. Create a 2-3 sentence summary that captures the key points
3. Focus on the main topic and important details
4. Keep it under 200 characters
5. If the content is insufficient, return a brief description of the title
6. Output ONLY the summary, no additional text

Summary:"""


def generate_summary_gemini(title: str, content: str) -> Optional[str]:
    """Generate summary using Google Gemini API.

    Args:
        title: Article title
        content: Article content

    Returns:
        Generated summary or None if failed
    """
    api_key = get_gemini_api_key()
    if not api_key:
        print("Gemini API key not configured, skipping AI summary")
        return None

    model = get_gemini_model()
    prompt = build_summary_prompt(title, content)

    url = f"{GEMINI_API_BASE}/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.7,
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()

            # Extract summary from response
            try:
                summary = data["candidates"][0]["content"]["parts"][0]["text"].strip()

                # Clean up common prefixes
                summary = re.sub(r'^(Summary:|요약:|요약\s*)', '', summary).strip()

                # Limit length
                if len(summary) > 300:
                    summary = summary[:297] + "..."

                return summary
            except (KeyError, IndexError) as e:
                print(f"Error parsing Gemini response: {e}")
                print(f"Response data: {data}")
                return None
        else:
            print(f"Gemini API returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None


# ============================================
# Main Summarization Pipeline
# ============================================

class ArticleSummarizer:
    """Main class for article summarization."""

    def __init__(self, enable_content_extraction: bool = True):
        """Initialize summarizer.

        Args:
            enable_content_extraction: If False, only summarize title/description
        """
        self.enable_content_extraction = enable_content_extraction
        self.api_key = get_gemini_api_key()

    def summarize_article(
        self,
        title: str,
        url: str,
        description: str = ""
    ) -> Optional[str]:
        """Generate summary for an article.

        Args:
            title: Article title
            url: Article URL
            description: Article description (from RSS feed)

        Returns:
            Generated summary or None if failed
        """
        if not self.api_key:
            return None

        # Try to extract full content if enabled
        content = ""

        if self.enable_content_extraction and url:
            content = extract_article_content(url)

        # Fall back to description if content extraction failed
        if not content:
            content = description or title

        # If we only have title, use it as content
        if not content:
            content = title

        # Generate summary
        summary = generate_summary_gemini(title, content)

        return summary

    def summarize_batch(
        self,
        articles: list[Dict[str, Any]]
    ) -> Dict[str, Optional[str]]:
        """Generate summaries for multiple articles.

        Args:
            articles: List of article dictionaries with title, link, description

        Returns:
            Dictionary mapping article URLs to summaries
        """
        if not self.api_key:
            return {}

        summaries = {}

        for article in articles:
            url = article.get("link", "")
            title = article.get("title", "")
            description = article.get("description", "")

            if not url or not title:
                continue

            try:
                summary = self.summarize_article(title, url, description)
                if summary:
                    summaries[url] = summary
            except Exception as e:
                print(f"Error summarizing {url}: {e}")

        return summaries


# ============================================
# Convenience Functions
# ============================================

def summarize_article(
    title: str,
    url: str,
    description: str = ""
) -> Optional[str]:
    """Convenience function to summarize a single article.

    Args:
        title: Article title
        url: Article URL
        description: Article description

    Returns:
        Generated summary or None if failed
    """
    summarizer = ArticleSummarizer()
    return summarizer.summarize_article(title, url, description)


def summarize_articles_batch(
    articles: list[Dict[str, Any]]
) -> Dict[str, Optional[str]]:
    """Convenience function to summarize multiple articles.

    Args:
        articles: List of article dictionaries

    Returns:
        Dictionary mapping article URLs to summaries
    """
    summarizer = ArticleSummarizer()
    return summarizer.summarize_batch(articles)
