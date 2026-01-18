"""Article Summarization module.

Extracts article content using Trafilatura and summarizes with Gemini AI.
"""

import os
import time
from typing import Optional, List

import trafilatura
from google import genai

from src.parser import Article


# Gemini 설정
GEMINI_MODEL = "gemini-2.0-flash"
MAX_CONTENT_LENGTH = 10000  # 본문 최대 길이 (토큰 비용 최적화)
RATE_LIMIT_DELAY = 0.5  # API 호출 간 대기 시간 (초)


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    return api_key


def get_gemini_client():
    """Initialize and return Gemini client."""
    api_key = get_gemini_api_key()
    return genai.Client(api_key=api_key)


def extract_article_content(url: str) -> Optional[str]:
    """URL에서 기사 본문 추출.
    
    Args:
        url: 기사 URL
        
    Returns:
        추출된 본문 텍스트, 실패시 None
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            return content
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
    return None


def summarize_with_gemini(content: str, title: str) -> Optional[str]:
    """Gemini로 기사 요약 생성.
    
    Args:
        content: 기사 본문
        title: 기사 제목
        
    Returns:
        생성된 요약, 실패시 None
    """
    try:
        client = get_gemini_client()
        
        # 본문이 너무 길면 잘라내기
        truncated_content = content[:MAX_CONTENT_LENGTH] if content else ""
        
        prompt = f"""다음 기사를 한국어로 2-3문장으로 간결하게 요약해주세요.
핵심 내용만 전달하고, 불필요한 서론이나 결론 없이 바로 요약을 시작하세요.
만약 본문이 영어라면 한국어로 번역하여 요약해주세요.

제목: {title}

본문:
{truncated_content}
"""
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing article '{title}': {e}")
    return None


def summarize_article(url: str, title: str) -> Optional[str]:
    """URL에서 본문 추출 후 요약 생성 (통합 함수).
    
    Args:
        url: 기사 URL
        title: 기사 제목
        
    Returns:
        생성된 요약, 실패시 None
    """
    content = extract_article_content(url)
    if not content:
        print(f"  Failed to extract content from: {url}")
        return None
    
    return summarize_with_gemini(content, title)


def summarize_articles(articles: List[Article], max_articles: int = None) -> List[Article]:
    """여러 기사에 대해 요약 생성.
    
    Args:
        articles: 요약할 기사 목록
        max_articles: 최대 요약 생성 개수 (None이면 전체)
        
    Returns:
        요약이 추가된 기사 목록
    """
    if not articles:
        return articles
    
    # API 키 확인
    try:
        get_gemini_api_key()
    except ValueError as e:
        print(f"Skipping summarization: {e}")
        return articles
    
    articles_to_process = articles[:max_articles] if max_articles else articles
    total = len(articles_to_process)
    
    print(f"\nGenerating summaries for {total} articles...")
    
    for i, article in enumerate(articles_to_process):
        summary = summarize_article(article["link"], article["title"])
        
        if summary:
            article["summary"] = summary
            print(f"  [{i+1}/{total}] ✓ {article['title'][:50]}...")
        else:
            article["summary"] = None
            print(f"  [{i+1}/{total}] ✗ {article['title'][:50]}...")
        
        # Rate limiting
        if i < total - 1:
            time.sleep(RATE_LIMIT_DELAY)
    
    success_count = sum(1 for a in articles_to_process if a.get("summary"))
    print(f"Summarization complete: {success_count}/{total} successful")
    
    return articles
