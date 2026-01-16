"""Tests for the notifier module."""

import pytest
from unittest.mock import patch, MagicMock
from src.notifier import format_message, send_discord_notification


class TestFormatMessage:
    """Test cases for format_message function."""
    
    def test_format_message_with_articles(self):
        """Should format articles as markdown list."""
        articles = [
            {'title': 'Test Article 1', 'link': 'https://example.com/1', 'published': None},
            {'title': 'Test Article 2', 'link': 'https://example.com/2', 'published': None},
        ]
        
        result = format_message(articles)
        
        assert '📰 **새로운 기사가 도착했습니다!**' in result
        assert '[Test Article 1](https://example.com/1)' in result
        assert '[Test Article 2](https://example.com/2)' in result
        assert '총 2개의 새 기사' in result
    
    def test_format_message_empty_list(self):
        """Should return empty string for empty list."""
        result = format_message([])
        
        assert result == ""
    
    def test_format_message_single_article(self):
        """Should format single article correctly."""
        articles = [
            {'title': 'Single Article', 'link': 'https://example.com/1', 'published': None},
        ]
        
        result = format_message(articles)
        
        assert '총 1개의 새 기사' in result


class TestSendDiscordNotification:
    """Test cases for send_discord_notification function."""
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_success(self, mock_post, mock_webhook):
        """Should return True on successful notification."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        articles = [
            {'title': 'Test', 'link': 'https://example.com/1', 'published': None},
        ]
        
        result = send_discord_notification(articles)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_failure(self, mock_post, mock_webhook):
        """Should return False on network error."""
        mock_post.side_effect = Exception("Network error")
        
        articles = [
            {'title': 'Test', 'link': 'https://example.com/1', 'published': None},
        ]
        
        result = send_discord_notification(articles)
        
        assert result is False
    
    def test_send_notification_empty_list(self):
        """Should return True for empty article list."""
        result = send_discord_notification([])
        
        assert result is True
