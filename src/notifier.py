"""Discord Notification module.

Sends article notifications via Discord Webhook.
"""

import requests
from typing import List
from src.config import get_discord_webhook_url
from src.parser import Article


def format_message(articles: List[Article]) -> str:
    """Format articles into a Discord-friendly markdown message.
    
    Args:
        articles: List of articles to format
        
    Returns:
        Formatted markdown string
    """
    if not articles:
        return ""
    
    lines = ["📰 **새로운 기사가 도착했습니다!**\n"]
    
    for article in articles:
        # Format: [Title](Link)
        lines.append(f"• [{article['title']}]({article['link']})")
    
    lines.append(f"\n총 {len(articles)}개의 새 기사")
    
    return "\n".join(lines)


def send_discord_notification(articles: List[Article]) -> bool:
    """Send notification to Discord via webhook.
    
    Args:
        articles: List of new articles to notify about
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    if not articles:
        print("No articles to notify")
        return True
    
    message = format_message(articles)
    
    # Discord webhook has a 2000 character limit
    # If message is too long, split into multiple messages
    if len(message) > 2000:
        return _send_chunked_notification(articles)
    
    try:
        response = requests.post(
            get_discord_webhook_url(),
            json={"content": message},
            timeout=10
        )
        response.raise_for_status()
        print(f"Successfully sent notification for {len(articles)} articles")
        return True
    except Exception as e:
        print(f"Error sending Discord notification: {e}")
        return False


def _send_chunked_notification(articles: List[Article]) -> bool:
    """Send notification in chunks if too long.
    
    Args:
        articles: List of articles to notify about
        
    Returns:
        True if all notifications sent successfully
    """
    chunk_size = 10  # Send 10 articles per message
    success = True
    
    for i in range(0, len(articles), chunk_size):
        chunk = articles[i:i + chunk_size]
        message = format_message(chunk)
        
        try:
            response = requests.post(
                get_discord_webhook_url(),
                json={"content": message},
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending chunk notification: {e}")
            success = False
    
    return success
