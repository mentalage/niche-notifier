"""Main entry point for Notify Niche RSS Collector.

Orchestrates the RSS collection, filtering, notification, and storage workflow.
"""

from src.config import FEED_CATEGORIES, is_ai_summary_enabled
from src.parser import parse_feeds_by_category
from src.db import filter_new_articles, save_article, sync_feeds_from_config
from src.notifier import send_discord_notification


def process_with_summaries(new_articles: list, new_by_category: dict) -> dict:
    """Generate AI summaries for new articles.

    Args:
        new_articles: List of new articles
        new_by_category: Articles grouped by category

    Returns:
        Updated new_by_category with summaries added
    """
    if not is_ai_summary_enabled():
        print("AI summary disabled, skipping...")
        return new_by_category

    print(f"\nGenerating AI summaries for {len(new_articles)} articles...")

    from src.summarizer import ArticleSummarizer

    summarizer = ArticleSummarizer()
    summaries = summarizer.summarize_batch(new_articles)

    if not summaries:
        print("No summaries generated")
        return new_by_category

    print(f"Generated {len(summaries)} summaries")

    # Add summaries to articles
    for category, articles in new_by_category.items():
        for article in articles:
            url = article.get("link", "")
            summary = summaries.get(url)
            if summary:
                article["summary"] = summary

    return new_by_category


def main() -> None:
    """Main execution function.

    Workflow:
    1. Sync feeds from config to database
    2. Parse feeds by category
    3. Each category applies its own keyword filters
    4. Filter out already processed articles
    5. Generate AI summaries (if enabled)
    6. Send category-grouped notification
    7. Save new articles to database
    """
    print("=== Notify Niche RSS Collector (Category-Based) ===")
    print(f"Processing {len(FEED_CATEGORIES)} categories...")

    if not FEED_CATEGORIES:
        print("Warning: No categories configured. Add categories to src/config.py")
        return

    # Step 1: Sync feeds from config to database
    sync_feeds_from_config(FEED_CATEGORIES)

    # Step 2 & 3: Parse feeds by category and apply keyword filters
    articles_by_category = parse_feeds_by_category(FEED_CATEGORIES)

    if not articles_by_category:
        print("No articles found in any category")
        return

    # Flatten articles for database filtering
    all_articles = []
    for articles in articles_by_category.values():
        all_articles.extend(articles)

    total_before = len(all_articles)
    print(f"\nTotal articles after filtering: {total_before}")

    # Step 3: Filter out already processed articles
    new_articles = filter_new_articles(all_articles)

    if not new_articles:
        print("No new articles to process")
        return

    # Group new articles back by category
    new_by_category = {}
    for article in new_articles:
        category = article.get("category", "기타")
        if category not in new_by_category:
            new_by_category[category] = []
        new_by_category[category].append(article)

    # Step 4: Generate AI summaries (if enabled)
    if is_ai_summary_enabled():
        new_by_category = process_with_summaries(new_articles, new_by_category)
    else:
        print("AI summary disabled (GEMINI_API_KEY not set)")

    # Step 5: Send notification
    notification_sent = send_discord_notification(new_by_category)

    if not notification_sent:
        print("Warning: Failed to send some notifications")

    # Step 6: Save articles to database
    saved_count = 0
    for category, articles in new_by_category.items():
        for article in articles:
            # Set summary_status based on whether summary was generated
            if article.get("summary"):
                article["summary_status"] = "completed"
            elif is_ai_summary_enabled():
                article["summary_status"] = "failed"
            else:
                article["summary_status"] = None

            if save_article(article):
                saved_count += 1

    print(f"\nSaved {saved_count}/{len(new_articles)} new articles to database")
    print("=== Execution complete ===")


if __name__ == "__main__":
    main()
