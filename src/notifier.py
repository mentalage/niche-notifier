"""Discord Notification module.

Sends article notifications via Discord Webhook with category grouping using embeds.
"""

import time
import requests
from typing import Dict, List
from src.config import get_discord_webhook_url, FEED_CATEGORIES
from src.parser import Article

# Discord API limits
MAX_EMBEDS_PER_MESSAGE = 10
MAX_EMBED_TITLE_LENGTH = 256
MAX_EMBED_DESCRIPTION_LENGTH = 4096

# Priority colors (Discord uses decimal color values)
PRIORITY_COLORS = {
    "high": 0xFF4444,    # Red
    "medium": 0xFFD700,  # Gold
    "low": 0x4499FF,     # Blue
    None: 0x808080       # Gray
}

# Priority icons
PRIORITY_ICONS = {
    "high": "🔥",
    "medium": "⭐",
    "low": "📌",
    None: "•"
}


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length with suffix.
    
    Args:
        text: The text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to append when truncated
        
    Returns:
        Truncated text with suffix if needed
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# Category header color (Discord dark theme)
CATEGORY_HEADER_COLOR = 0x2F3136


def build_category_header_embed(category_name: str, emoji: str, article_count: int) -> dict:
    """Build a Discord embed for category header.
    
    Args:
        category_name: Name of the category
        emoji: Category emoji
        article_count: Number of articles in this category
        
    Returns:
        Discord embed dictionary for category header
    """
    return {
        "title": f"{emoji} {category_name}",
        "description": f"{article_count}개의 새로운 기사",
        "color": CATEGORY_HEADER_COLOR,
    }


def build_article_embed(article: Article, category_name: str, emoji: str) -> dict:
    """Build a Discord embed for a single article.
    
    Args:
        article: Article dictionary with title, link, description, priority
        category_name: Name of the category for footer
        emoji: Category emoji for footer
        
    Returns:
        Discord embed dictionary
    """
    priority = article.get("priority")
    color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS[None])
    icon = PRIORITY_ICONS.get(priority, "•")
    
    # Truncate title and description
    title = truncate_text(article['title'], MAX_EMBED_TITLE_LENGTH - len(icon) - 1)
    
    # 요약이 있으면 요약 사용, 없으면 description 사용
    summary = article.get("summary")
    description = summary if summary else article.get("description", "")
    if description:
        description = truncate_text(description, 500)  # Use 500 chars for cleaner display
    
    # Build footer text with optional feed name
    footer_text = f"{emoji} {category_name}"
    feed_name = article.get("feed_name")
    if feed_name:
        footer_text += f" - {feed_name}"
    
    embed = {
        "title": f"{icon} {title}",
        "url": article['link'],
        "color": color,
        "footer": {
            "text": footer_text
        }
    }
    
    if description:
        embed["description"] = description
    
    return embed


def chunk_embeds(embeds: List[dict], max_per_chunk: int = MAX_EMBEDS_PER_MESSAGE) -> List[List[dict]]:
    """Split embeds into chunks of max_per_chunk size.
    
    Args:
        embeds: List of embed dictionaries
        max_per_chunk: Maximum embeds per chunk (default: 10)
        
    Returns:
        List of embed chunks
    """
    if not embeds:
        return []
    
    chunks = []
    for i in range(0, len(embeds), max_per_chunk):
        chunks.append(embeds[i:i + max_per_chunk])
    return chunks


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
    
    # Build all embeds
    all_embeds = []
    total_count = 0
    category_counts = []
    
    for category_name, articles in articles_by_category.items():
        if not articles:
            continue
        
        # Get category emoji
        category_config = FEED_CATEGORIES.get(category_name, {})
        emoji = category_config.get("emoji", "📂")
        
        # Add category header embed
        header_embed = build_category_header_embed(category_name, emoji, len(articles))
        all_embeds.append(header_embed)
        
        # Build embeds for each article (limits already applied per-feed in parser)
        for article in articles:
            embed = build_article_embed(article, category_name, emoji)
            all_embeds.append(embed)
        
        total_count += len(articles)
        category_counts.append(f"{category_name} {len(articles)}")
    
    if not all_embeds:
        print("No embeds to send")
        return True
    
    # Chunk embeds for multiple messages if needed
    embed_chunks = chunk_embeds(all_embeds)
    
    # Summary text for the first message
    summary = ", ".join(category_counts)
    header_content = f"📰 **새로운 기사가 도착했습니다!** (총 {total_count}개: {summary})"
    
    # Send each chunk
    webhook_url = get_discord_webhook_url()
    success = True
    
    for i, chunk in enumerate(embed_chunks):
        payload = {"embeds": chunk}
        
        # Add header content only to the first message
        if i == 0:
            payload["content"] = header_content
        
        # Retry logic for failed requests
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                print(f"Successfully sent notification chunk {i + 1}/{len(embed_chunks)}")
                
                # Add delay between chunks to avoid rate limiting
                if i < len(embed_chunks) - 1:
                    time.sleep(1)
                break  # Success, exit retry loop
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries} for chunk {i + 1}: {e}")
                    time.sleep(2)  # Wait before retry
                else:
                    print(f"Error sending Discord notification chunk {i + 1} after {max_retries} attempts: {e}")
                    success = False
    
    if success:
        print(f"Successfully sent all notifications for {total_count} articles")
    
    return success
