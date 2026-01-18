"""Configuration module for Notify Niche.

Loads environment variables and defines RSS feed URLs.
Supports external YAML configuration for feeds.
"""

import os
from typing import Optional
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# YAML config file path (project root)
FEEDS_CONFIG_PATH = Path(__file__).parent.parent / "feeds.yaml"


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


def load_feed_categories(config_path: Path = None) -> dict:
    """Load feed categories from YAML file or use defaults.
    
    Args:
        config_path: Path to YAML config file (defaults to FEEDS_CONFIG_PATH)
        
    Returns:
        Dictionary of feed category configurations
    """
    path = config_path or FEEDS_CONFIG_PATH
    
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                categories = yaml.safe_load(f)
                if categories:
                    print(f"Loaded feed config from {path}")
                    return categories
        except Exception as e:
            print(f"Error loading {path}: {e}, using defaults")
    
    return DEFAULT_FEED_CATEGORIES


# Default Category-Based RSS Feed Configuration (fallback)
# Used when feeds.yaml is not present or has errors
# feeds can be either:
#   - string: URL only (backward compatible)
#   - dict: {"url": "...", "name": "..."} with display name
DEFAULT_FEED_CATEGORIES = {
    "개발": {
        "enabled": True,
        "emoji": "💻",
        "feeds": [
            # Hacker News
            {"url": "https://hnrss.org/show", "name": "HN Show"},
            {"url": "https://hnrss.org/newest?q=AI", "name": "HN AI"},
            {"url": "https://hnrss.org/best", "name": "HN Best"},
            
            # GeekNews (한국 개발자 커뮤니티)
            {"url": "https://feeds.feedburner.com/geeknews-feed", "name": "GeekNews"},
            
            # 44bits (클라우드/데브옵스)
            {"url": "https://44bits.io/feed.xml", "name": "44bits"},
            
            # Outsider's Dev Story
            {"url": "https://blog.outsider.ne.kr/rss", "name": "Outsider"},
            
            # 카카오 기술블로그
            {"url": "https://tech.kakao.com/feed/", "name": "카카오"},
            
            # 우아한형제들 기술블로그
            {"url": "https://techblog.woowahan.com/feed/", "name": "우아한형제들"},
            
            # 토스 기술블로그
            {"url": "https://toss.tech/rss.xml", "name": "토스"},
            
            # 네이버 D2
            {"url": "https://d2.naver.com/d2.atom", "name": "네이버 D2"},
            
            # 라인 기술블로그
            {"url": "https://engineering.linecorp.com/ko/feed/", "name": "LINE"},
            
            # 당근 기술블로그
            {"url": "https://medium.com/feed/daangn", "name": "당근"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "AI", "ChatGPT", "GPT", "Gemini", "LLM", "Claude",
                "인공지능", "딥러닝", "Deep Learning", "RAG"
            ],
            "medium_priority": [
                "Python", "Docker", "AWS", "Kubernetes", "머신러닝",
                "TypeScript", "React", "Next.js", "Spring", "Kotlin"
            ],
            "low_priority": [
                "프로그래밍", "개발", "코딩", "아키텍처", "MSA"
            ],
            "exclude": [
                "광고", "스폰서", "홍보", "제휴", "채용"
            ]
        }
    },
    
    "주식/경제": {
        "enabled": True,
        "emoji": "📈",
        "feeds": [
            # 미국 주식/경제
            {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC", "name": "Yahoo S&P500"},
            {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "name": "CNBC"},
            {"url": "https://feeds.bloomberg.com/markets/news.rss", "name": "Bloomberg"},
            
            # Seeking Alpha (미국 주식 분석)
            {"url": "https://seekingalpha.com/market_currents.xml", "name": "Seeking Alpha"},
            
            # 한국 경제
            {"url": "https://www.hankyung.com/feed/all-news", "name": "한국경제"},
            {"url": "https://rss.etnews.com/Section901.xml", "name": "전자신문"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "NVIDIA", "엔비디아", "Tesla", "테슬라", "Apple", "애플",
                "Microsoft", "마이크로소프트", "Google", "구글", "Amazon", "아마존",
                "반도체", "AI주", "빅테크", "나스닥", "NASDAQ", "S&P"
            ],
            "medium_priority": [
                "주가", "실적", "IPO", "공모주", "배당", "ETF",
                "금리", "Fed", "연준", "인플레이션", "GDP"
            ],
            "low_priority": [
                "투자", "증시", "코스피", "코스닥", "다우", "환율"
            ],
            "exclude": [
                "광고", "스폰서", "보험", "대출", "카드추천"
            ]
        }
    },
    
    "기술블로그": {
        "enabled": True,
        "emoji": "🔧",
        "feeds": [
            # 개인 기술 블로그
            {"url": "https://blog.outsider.ne.kr/rss", "name": "Outsider"},
            {"url": "https://jojoldu.tistory.com/rss", "name": "향로"},
            {"url": "https://cheese10yun.github.io/feed.xml", "name": "Cheese10"},
            
            # 해외 유명 블로그
            {"url": "https://martinfowler.com/feed.atom", "name": "Martin Fowler"},
            {"url": "https://blog.pragmaticengineer.com/rss/", "name": "Pragmatic Engineer"},
        ],
        "keyword_filters": {
            "enabled": False,  # 모든 글 받기
        }
    },
    
    "블로그": {
        "enabled": True,
        "emoji": "📝",
        "feeds": [
            {"url": "https://rss.blog.naver.com/ranto28.xml", "name": "개인블로그"},
        ],
        "keyword_filters": {
            "enabled": False,
        }
    },
}

# Load from YAML file or use defaults
FEED_CATEGORIES = load_feed_categories()
