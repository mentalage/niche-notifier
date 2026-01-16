"""Discord Notification module.

Sends article notifications via Discord Webhook with category grouping.
"""

import requests
from typing import Dict, List
from src.config import get_discord_webhook_url, FEED_CATEGORIES
from src.parser import Article


def send_discord_notification(articles_by_category: Dict[str, List[Article]]) -> bool:
    """Send notification to Discord via webhook with category grouping.
    
    Args:
        articles_by_category: Dictionary mapping category names to article lists
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    if not articles_by_category:
        print("No articles to notify")
        return True
    
    # Priority icon mapping
    priority_icons = {
        "high": "🔥",
        "medium": "⭐",
        "low": "📌",
        None: "•"
    }
    
    # Build message with category sections
    lines = ["📰 **새로운 기사가 도착했습니다!**\n"]
    total_count = 0
    category_counts = []
    
    for category_name, articles in articles_by_category.items():
        if not articles:
            continue
        
        # Get category emoji
        category_config = FEED_CATEGORIES.get(category_name, {})
        emoji = category_config.get("emoji", "📂")
        
        # Category header
        lines.append(f"{emoji} **【{category_name}】**")
        
        # Articles in this category
        for article in articles:
            priority = article.get("priority")
            icon = priority_icons.get(priority, "•")
            lines.append(f"{icon} [{article['title']}]({article['link']})")
        
        lines.append("")  # Empty line between categories
        total_count += len(articles)
        category_counts.append(f"{category_name} {len(articles)}")
    
    # Summary line
    summary = ", ".join(category_counts)
    lines.append(f"총 {total_count}개 ({summary})")
    
    message = "\n".join(lines)
    
    # Send message
    try:
        response = requests.post(
            get_discord_webhook_url(),
            json={"content": message},
            timeout=10
        )
        response.raise_for_status()
        print(f"Successfully sent notification for {total_count} articles")
        return True
    except Exception as e:
        print(f"Error sending Discord notification: {e}")
        return False
