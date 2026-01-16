"""Configuration module for Notify Niche.

Loads environment variables and defines RSS feed URLs.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


def get_env_var(name: str, required: bool = True) -> Optional[str]:
    """Get environment variable with optional requirement check.
    
    Args:
        name: Name of the environment variable
        required: If True, raises error when variable is missing
        
    Returns:
        The environment variable value or None
        
    Raises:
        ValueError: If required variable is not set
    """
    value = os.environ.get(name)
    if required and not value:
        raise ValueError(f"Required environment variable '{name}' is not set")
    return value


def get_supabase_url() -> str:
    """Get Supabase URL from environment."""
    return get_env_var("SUPABASE_URL") or ""


def get_supabase_key() -> str:
    """Get Supabase Key from environment."""
    return get_env_var("SUPABASE_KEY") or ""


def get_discord_webhook_url() -> str:
    """Get Discord Webhook URL from environment."""
    return get_env_var("DISCORD_WEBHOOK_URL") or ""


# Category-Based RSS Feed Configuration
# Each category has its own feeds and keyword filters
FEED_CATEGORIES = {
    "개발": {
        "enabled": True,
        "emoji": "💻",
        "feeds": [
            "https://hnrss.org/show",
            "https://hnrss.org/newest?q=AI",
            "https://hnrss.org/best",
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "AI", "ChatGPT", "GPT", "Gemini", "LLM",
                "인공지능", "Artificial Intelligence", "딥러닝", "Deep Learning"
            ],
            "medium_priority": [
                "Python", "Docker", "AWS", "Kubernetes", "머신러닝", "Machine Learning",
                "프론트엔드", "Frontend", "백엔드", "Backend", "DevOps"
            ],
            "low_priority": [
                "프로그래밍", "Programming", "개발", "Development", 
                "코딩", "Coding", "웹", "Web", "앱", "App"
            ],
            "exclude": [
                "광고", "Ad", "Advertisement", "스폰서", "Sponsor",
                "홍보", "Promotion", "제휴", "Affiliate"
            ]
        }
    },
    "블로그": {
        "enabled": True,
        "emoji": "📝",
        "feeds": [
            "https://rss.blog.naver.com/ranto28.xml",
        ],
        "keyword_filters": {
            "enabled": False,  # 모든 블로그 글 받기
        }
    }
}

