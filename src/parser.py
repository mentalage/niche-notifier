"""RSS Feed Parser module.

Parses RSS feeds and extracts article information.
"""

import feedparser
from typing import TypedDict, List, Optional


import re

# Maximum articles to fetch per RSS feed
MAX_ARTICLES_PER_FEED = 10


class Article(TypedDict):
    """Type definition for an article."""
    title: str
    link: str
    description: Optional[str]  # Added description
    published: Optional[str]
    priority: Optional[str]  # 'high', 'medium', 'low', or None
    category: Optional[str]  # Category name
    feed_url: Optional[str]  # Source feed URL
    feed_name: Optional[str]  # Display name of the feed


def clean_html(raw_html: str) -> str:
    """Remove HTML tags and clean up whitespace.
    
    Args:
        raw_html: String containing HTML tags
        
    Returns:
        Cleaned text string
    """
    if not raw_html:
        return ""
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', raw_html)
    # Replace multiple whitespaces/newlines with a single space
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text


def parse_feed(url: str, feed_name: str = None, max_articles: int = MAX_ARTICLES_PER_FEED) -> List[Article]:
    """Parse a single RSS feed and extract articles.
    
    Args:
        url: RSS feed URL to parse
        feed_name: Display name of the feed
        max_articles: Maximum number of articles to return per feed
        
    Returns:
        List of articles with title, link, description, and published date
    """
    articles: List[Article] = []
    
    try:
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # Get description or summary
            raw_description = entry.get("summary") or entry.get("description") or ""
            description = clean_html(raw_description)
            
            article: Article = {
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "description": description,
                "published": entry.get("published", None),
                "priority": None,  # Will be set by keyword filter
                "category": None,  # Will be set when parsing by category
                "feed_url": url,   # Track source feed URL
                "feed_name": feed_name,  # Track feed display name
            }
            
            if article["link"]:  # Only include entries with valid links
                articles.append(article)
                
    except Exception as e:
        print(f"Error parsing feed {url}: {e}")
    
    # Limit articles per feed
    return articles[:max_articles]


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


def filter_articles_by_keywords(
    articles: List[Article], 
    keywords_config: dict
) -> List[Article]:
    """Filter articles based on keyword configuration.
    
    Args:
        articles: List of articles to filter
        keywords_config: Dictionary containing keyword filtering rules
        
    Returns:
        Filtered list of articles with priority field set
    """
    # If filtering is disabled, return all articles
    if not keywords_config.get("enabled", True):
        return articles
    
    # If no keywords configured, return all articles
    has_keywords = any([
        keywords_config.get("high_priority"),
        keywords_config.get("medium_priority"),
        keywords_config.get("low_priority")
    ])
    
    if not has_keywords:
        return articles
    
    filtered_articles: List[Article] = []
    exclude_keywords = keywords_config.get("exclude", [])
    
    for article in articles:
        title_lower = article["title"].lower()
        
        # Check exclude keywords first
        should_exclude = any(
            keyword.lower() in title_lower 
            for keyword in exclude_keywords
        )
        
        if should_exclude:
            continue
        
        # Check priority keywords (high -> medium -> low)
        priority = None
        
        for keyword in keywords_config.get("high_priority", []):
            if keyword.lower() in title_lower:
                priority = "high"
                break
        
        if not priority:
            for keyword in keywords_config.get("medium_priority", []):
                if keyword.lower() in title_lower:
                    priority = "medium"
                    break
        
        if not priority:
            for keyword in keywords_config.get("low_priority", []):
                if keyword.lower() in title_lower:
                    priority = "low"
                    break
        
        # Only include articles that matched at least one keyword
        if priority:
            article["priority"] = priority
            filtered_articles.append(article)
    
    return filtered_articles


def parse_feeds_by_category(categories: dict) -> dict:
    """Parse RSS feeds organized by category.
    
    Args:
        categories: Dictionary of category configurations
        
    Returns:
        Dictionary mapping category names to lists of filtered articles
    """
    from typing import Dict
    
    results: Dict[str, List[Article]] = {}
    
    for category_name, config in categories.items():
        # Skip disabled categories
        if not config.get("enabled", True):
            print(f"Skipping disabled category: {category_name}")
            continue
        
        feeds = config.get("feeds", [])
        if not feeds:
            print(f"No feeds configured for category: {category_name}")
            continue
        
        print(f"\n=== Processing category: {category_name} ===")
        
        # Parse all feeds in this category
        category_articles: List[Article] = []
        for feed in feeds:
            # Support both string URLs and dict format {url, name}
            if isinstance(feed, dict):
                feed_url = feed.get("url", "")
                feed_name = feed.get("name")
            else:
                feed_url = feed
                feed_name = None
            
            if not feed_url:
                continue
            
            articles = parse_feed(feed_url, feed_name=feed_name)
            
            # Set category for each article
            for article in articles:
                article["category"] = category_name
            
            category_articles.extend(articles)
            print(f"Parsed {len(articles)} articles from {feed_name or feed_url}")
        
        print(f"Total {len(category_articles)} articles in category: {category_name}")
        
        # Apply keyword filtering for this category
        keyword_config = config.get("keyword_filters", {})
        filtered_articles = filter_articles_by_keywords(
            category_articles, 
            keyword_config
        )
        
        print(f"After filtering: {len(filtered_articles)} articles")
        
        if filtered_articles:
            results[category_name] = filtered_articles
    
    return results

