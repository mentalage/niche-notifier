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


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment."""
    return get_env_var("GEMINI_API_KEY", required=False) or ""


def get_gemini_model() -> str:
    """Get Gemini model name from environment (default: gemini-2.0-flash-exp)."""
    return get_env_var("GEMINI_MODEL", required=False) or "gemini-2.0-flash-exp"


def is_ai_summary_enabled() -> bool:
    """Check if AI summary feature is enabled."""
    return bool(get_gemini_api_key())


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
    
    "정보기술": {
        "enabled": True,
        "emoji": "💻",
        "parent": "주식/경제",
        "description": "소프트웨어, 하드웨어, 반도체, IT 서비스",
        "gics_sector": "Information Technology",
        "feeds": [
            {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC", "name": "Yahoo S&P500"},
            {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "name": "CNBC Tech"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "NVIDIA", "엔비디아", "Apple", "애플",
                "Microsoft", "마이크로소프트", "Google", "구글", "반도체", "Semiconductor",
                "AI주", "Chip", "TSMC", "AMD", "Intel"
            ],
            "medium_priority": [
                "소프트웨어", "Software", "클라우드", "Cloud", "SaaS", "데이터센터"
            ],
            "low_priority": ["IT", "테크", "Tech"],
            "exclude": ["광고", "Advertisement"]
        }
    },

    "통신서비스": {
        "enabled": True,
        "emoji": "📡",
        "parent": "주식/경제",
        "description": "통신, 미디어, 엔터테인먼트",
        "gics_sector": "Communication Services",
        "feeds": [
            {"url": "https://feeds.bloomberg.com/markets/news.rss", "name": "Bloomberg Media"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "Meta", "Facebook", "Netflix", "디즈니", "Disney", "유튜브", "YouTube", "알파벳"
            ],
            "medium_priority": ["스트리밍", "Streaming", "미디어", "Media", "방송"],
            "low_priority": ["통신", "Telecom"],
            "exclude": []
        }
    },

    "금융": {
        "enabled": True,
        "emoji": "🏦",
        "parent": "주식/경제",
        "description": "은행, 보험, 증권, 카드",
        "gics_sector": "Financials",
        "feeds": [
            {"url": "https://seekingalpha.com/market_currents.xml", "name": "Seeking Alpha"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "JPMorgan", "Bank of America", "워런 버핏", "Berkshire Hathaway", "비자", "Visa"
            ],
            "medium_priority": ["은행", "Bank", "금리", "Fed", "연준", "ETF"],
            "low_priority": ["금융", "Finance"],
            "exclude": []
        }
    },

    "헬스케어": {
        "enabled": True,
        "emoji": "🏥",
        "parent": "주식/경제",
        "description": "제약, 바이오, 의료기기",
        "gics_sector": "Health Care",
        "feeds": [],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "Johnson & Johnson", "Pfizer", "화이자", "Moderna", "모더나", "바이오"
            ],
            "medium_priority": ["백신", "Vaccine", "임상", "Clinical", "FDA"],
            "low_priority": ["의료", "Healthcare"],
            "exclude": []
        }
    },

    "임의소비재": {
        "enabled": True,
        "emoji": "🛍️",
        "parent": "주식/경제",
        "description": "자동차, 리테일, 레저, 호텔",
        "gics_sector": "Consumer Discretionary",
        "feeds": [
            {"url": "https://www.hankyung.com/feed/all-news", "name": "한국경제"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": [
                "Tesla", "테슬라", "Amazon", "아마존", "McDonald's", "맥도날드", "Nike"
            ],
            "medium_priority": ["리테일", "Retail", "전자상거래", "E-commerce"],
            "low_priority": ["소비재", "Consumer"],
            "exclude": []
        }
    },

    "에너지": {
        "enabled": True,
        "emoji": "⛽",
        "parent": "주식/경제",
        "description": "석유, 가스, 에너지 설비",
        "gics_sector": "Energy",
        "feeds": [],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["Exxon", "Chevron", "원유", "Crude Oil", "천연가스"],
            "medium_priority": ["석유", "Oil", "에너지", "Energy", "OPEC"],
            "low_priority": ["정유", "Refinery"],
            "exclude": []
        }
    },

    "산업재": {
        "enabled": True,
        "emoji": "🏭",
        "parent": "주식/경제",
        "description": "항공우주, 방산, 건설, 물류",
        "gics_sector": "Industrials",
        "feeds": [
            {"url": "https://rss.etnews.com/Section901.xml", "name": "전자신문"},
        ],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["Boeing", "보잉", "Lockheed", "방산", "Defense", "항공"],
            "medium_priority": ["건설", "Construction", "물류", "Logistics"],
            "low_priority": ["산업", "Industry"],
            "exclude": []
        }
    },

    "필수소비재": {
        "enabled": True,
        "emoji": "🛒",
        "parent": "주식/경제",
        "description": "식품, 음료, household products",
        "gics_sector": "Consumer Staples",
        "feeds": [],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["Coca-Cola", "코카콜라", "Pepsi", "펩시", "Walmart", "월마트"],
            "medium_priority": ["식품", "Food", "음료", "Beverage"],
            "low_priority": ["소비재", "Staples"],
            "exclude": []
        }
    },

    "공공요금": {
        "enabled": True,
        "emoji": "⚡",
        "parent": "주식/경제",
        "description": "전력, 가스, 수도",
        "gics_sector": "Utilities",
        "feeds": [],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["전력", "Electricity", "발전", "Power Generation"],
            "medium_priority": ["가스", "수도", "Utility"],
            "low_priority": ["공공", "Public"],
            "exclude": []
        }
    },

    "부동산": {
        "enabled": True,
        "emoji": "🏠",
        "parent": "주식/경제",
        "description": "부동산, REITs",
        "gics_sector": "Real Estate",
        "feeds": [],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["REIT", "리츠", "Prologis"],
            "medium_priority": ["주택", "Housing", "상업용 부동산", "Commercial"],
            "low_priority": ["부동산", "Real Estate"],
            "exclude": []
        }
    },

    "소재": {
        "enabled": True,
        "emoji": "🔩",
        "parent": "주식/경제",
        "description": "화학, 금속, 건축자재",
        "gics_sector": "Materials",
        "feeds": [],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["Dow", "다우", "화학", "Chemical", "철강", "Steel"],
            "medium_priority": ["금속", "Metal", "자재", "Materials"],
            "low_priority": ["소재"],
            "exclude": []
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
