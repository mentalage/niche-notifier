"""RSS Feed Parser module.

Parses RSS feeds and extracts article information.
"""

import feedparser
from typing import TypedDict, List, Optional


class Article(TypedDict):
    """Type definition for an article."""
    title: str
    link: str
    published: Optional[str]


def parse_feed(url: str) -> List[Article]:
    """Parse a single RSS feed and extract articles.
    
    Args:
        url: RSS feed URL to parse
        
    Returns:
        List of articles with title, link, and published date
    """
    articles: List[Article] = []
    
    try:
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            article: Article = {
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "published": entry.get("published", None),
            }
            
            if article["link"]:  # Only include entries with valid links
                articles.append(article)
                
    except Exception as e:
        print(f"Error parsing feed {url}: {e}")
    
    return articles


def parse_all_feeds(urls: List[str]) -> List[Article]:
    """Parse multiple RSS feeds and combine results.
    
    Args:
        urls: List of RSS feed URLs to parse
        
    Returns:
        Combined list of articles from all feeds
    """
    all_articles: List[Article] = []
    
    for url in urls:
        articles = parse_feed(url)
        all_articles.extend(articles)
        print(f"Parsed {len(articles)} articles from {url}")
    
    return all_articles
