"""Tests for the notifier module."""

import pytest
from unittest.mock import patch, MagicMock
from src.notifier import send_discord_notification


class TestSendDiscordNotification:
    """Test cases for send_discord_notification function."""
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_success(self, mock_post, mock_webhook):
        """Should return True on successful notification."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        articles_by_category = {
            "개발": [
                {'title': 'Test', 'link': 'https://example.com/1', 'published': None, 'priority': 'high', 'category': '개발'},
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_failure(self, mock_post, mock_webhook):
        """Should return False on network error."""
        mock_post.side_effect = Exception("Network error")
        
        articles_by_category = {
            "개발": [
                {'title': 'Test', 'link': 'https://example.com/1', 'published': None, 'priority': 'high', 'category': '개발'},
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is False
    
    def test_send_notification_empty_dict(self):
        """Should return True for empty category dict."""
        result = send_discord_notification({})
        
        assert result is True
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_multiple_categories(self, mock_post, mock_webhook):
        """Should format message with multiple categories."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        articles_by_category = {
            "개발": [
                {'title': 'Dev Article', 'link': 'https://example.com/1', 'published': None, 'priority': 'high', 'category': '개발'},
            ],
            "블로그": [
                {'title': 'Blog Post', 'link': 'https://example.com/2', 'published': None, 'priority': None, 'category': '블로그'},
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        # Check that the message includes category markers
        call_args = mock_post.call_args
        message_content = call_args[1]['json']['content']
        assert '【개발】' in message_content
        assert '【블로그】' in message_content
