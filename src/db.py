"""Supabase Database module.

Handles article storage and duplicate detection.
"""

from typing import List, Set
from supabase import create_client, Client
from src.config import get_supabase_url, get_supabase_key
from src.parser import Article

# Table name for processed articles
TABLE_NAME = "processed_articles"


def get_client() -> Client:
    """Create and return Supabase client.
    
    Returns:
        Supabase client instance
    """
    return create_client(get_supabase_url(), get_supabase_key())


def get_processed_links() -> Set[str]:
    """Get all processed article links from database.
    
    Returns:
        Set of links that have already been processed
    """
    client = get_client()
    
    try:
        response = client.table(TABLE_NAME).select("link").execute()
        return {row["link"] for row in response.data}
    except Exception as e:
        print(f"Error fetching processed links: {e}")
        return set()


def save_article(article: Article) -> bool:
    """Save a new article to the database.
    
    Args:
        article: Article data to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    client = get_client()
    
    try:
        client.table(TABLE_NAME).upsert({
            "link": article["link"],
            "title": article["title"],
            "published_at": article["published"],
            "category": article.get("category"),
            "priority": article.get("priority"),
        }, on_conflict="link").execute()
        return True
    except Exception as e:
        print(f"Error saving article: {e}")
        return False


def filter_new_articles(articles: List[Article]) -> List[Article]:
    """Filter out articles that have already been processed.
    
    Args:
        articles: List of articles to filter
        
    Returns:
        List of new articles not in database
    """
    # Deduplicate input articles by link
    unique_articles = {}
    for article in articles:
        link = article["link"]
        if link not in unique_articles:
            unique_articles[link] = article
    
    processed_links = get_processed_links()
    
    new_articles = [
        article for link, article in unique_articles.items()
        if link not in processed_links
    ]
    
    print(f"Found {len(new_articles)} new articles out of {len(articles)} total (deduplicated: {len(unique_articles)})")
    return new_articles


# ============================================
# Feeds Table Management (for future Web UI)
# ============================================

FEEDS_TABLE = "feeds"


def get_feeds(category: str = None, enabled_only: bool = True) -> List[dict]:
    """Get all RSS feeds from database.
    
    Args:
        category: Optional category filter
        enabled_only: If True, only return enabled feeds
        
    Returns:
        List of feed dictionaries
    """
    client = get_client()
    
    try:
        query = client.table(FEEDS_TABLE).select("*")
        
        if category:
            query = query.eq("category", category)
        
        if enabled_only:
            query = query.eq("enabled", True)
        
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error fetching feeds: {e}")
        return []


def add_feed(url: str, category: str, name: str = None) -> bool:
    """Add a new RSS feed to the database.
    
    Args:
        url: RSS feed URL
        category: Category name for the feed
        name: Optional display name for the feed
        
    Returns:
        True if added successfully, False otherwise
    """
    client = get_client()
    
    try:
        client.table(FEEDS_TABLE).insert({
            "url": url,
            "category": category,
            "name": name,
            "enabled": True,
        }).execute()
        print(f"Added feed: {url}")
        return True
    except Exception as e:
        print(f"Error adding feed: {e}")
        return False


def remove_feed(url: str) -> bool:
    """Remove a RSS feed from the database.
    
    Args:
        url: RSS feed URL to remove
        
    Returns:
        True if removed successfully, False otherwise
    """
    client = get_client()
    
    try:
        client.table(FEEDS_TABLE).delete().eq("url", url).execute()
        print(f"Removed feed: {url}")
        return True
    except Exception as e:
        print(f"Error removing feed: {e}")
        return False


def update_feed(url: str, updates: dict) -> bool:
    """Update a RSS feed's properties.
    
    Args:
        url: RSS feed URL to update
        updates: Dictionary of fields to update (name, category, enabled)
        
    Returns:
        True if updated successfully, False otherwise
    """
    client = get_client()
    
    # Only allow specific fields to be updated
    allowed_fields = {"name", "category", "enabled", "last_fetched_at"}
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not filtered_updates:
        print("No valid fields to update")
        return False
    
    try:
        client.table(FEEDS_TABLE).update(filtered_updates).eq("url", url).execute()
        print(f"Updated feed: {url}")
        return True
    except Exception as e:
        print(f"Error updating feed: {e}")
        return False


def sync_feeds_from_config(categories: dict) -> int:
    """Sync RSS feeds from config to database.
    
    This function ensures all feeds defined in config.py are stored in the
    feeds table. Uses upsert to avoid duplicates and update names.
    
    Args:
        categories: Dictionary of category configurations from config.py
        
    Returns:
        Number of feeds synced
    """
    client = get_client()
    synced_count = 0
    
    for category_name, config in categories.items():
        if not config.get("enabled", True):
            continue
        
        feeds = config.get("feeds", [])
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
            
            try:
                client.table(FEEDS_TABLE).upsert({
                    "url": feed_url,
                    "name": feed_name,
                    "category": category_name,
                    "enabled": True,
                }, on_conflict="url").execute()
                synced_count += 1
            except Exception as e:
                print(f"Error syncing feed {feed_url}: {e}")
    
    print(f"Synced {synced_count} feeds to database")
    return synced_count


