"""Main entry point for Notify Niche RSS Collector.

Orchestrates the RSS collection, filtering, notification, and storage workflow.
"""

from src.config import FEED_URLS
from src.parser import parse_all_feeds
from src.db import filter_new_articles, save_article
from src.notifier import send_discord_notification


def main() -> None:
    """Main execution function.
    
    Workflow:
    1. Parse all configured RSS feeds
    2. Filter out already processed articles
    3. Send Discord notification for new articles
    4. Save new articles to database
    """
    print("=== Notify Niche RSS Collector ===")
    print(f"Processing {len(FEED_URLS)} feeds...")
    
    if not FEED_URLS:
        print("Warning: No RSS feed URLs configured. Add feeds to src/config.py")
        return
    
    # Step 1: Parse all feeds
    articles = parse_all_feeds(FEED_URLS)
    print(f"Total articles parsed: {len(articles)}")
    
    if not articles:
        print("No articles found in feeds")
        return
    
    # Step 2: Filter new articles
    new_articles = filter_new_articles(articles)
    
    if not new_articles:
        print("No new articles to process")
        return
    
    # Step 3: Send notification
    notification_sent = send_discord_notification(new_articles)
    
    if not notification_sent:
        print("Warning: Failed to send some notifications")
    
    # Step 4: Save articles to database
    saved_count = 0
    for article in new_articles:
        if save_article(article):
            saved_count += 1
    
    print(f"Saved {saved_count}/{len(new_articles)} new articles to database")
    print("=== Execution complete ===")


if __name__ == "__main__":
    main()
