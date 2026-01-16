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
        client.table(TABLE_NAME).insert({
            "link": article["link"],
            "title": article["title"],
            "published_at": article["published"],
        }).execute()
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
    processed_links = get_processed_links()
    
    new_articles = [
        article for article in articles 
        if article["link"] not in processed_links
    ]
    
    print(f"Found {len(new_articles)} new articles out of {len(articles)} total")
    return new_articles
