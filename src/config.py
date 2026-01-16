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


# RSS Feed URLs to monitor
# TODO: Add your RSS feed URLs here
FEED_URLS = [
    # 메르의 블로그
    "https://rss.blog.naver.com/ranto28.xml",
    
    # Hacker News
    "https://hnrss.org/show", # 새로운 프로젝트
    "https://hnrss.org/newest?q=AI", # AI 관련 모니터링
    "https://hnrss.org/best",  # 인기 있는 프로젝트
]
