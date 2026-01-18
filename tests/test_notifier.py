"""Tests for the notifier module."""

import pytest
from unittest.mock import patch, MagicMock
from src.notifier import (
    send_discord_notification,
    truncate_text,
    build_article_embed,
    chunk_embeds,
    MAX_EMBED_TITLE_LENGTH,
    MAX_EMBEDS_PER_MESSAGE,
    PRIORITY_COLORS
)


class TestTruncateText:
    """Test cases for truncate_text function."""
    
    def test_truncate_short_text(self):
        """Should return text as-is when under limit."""
        result = truncate_text("Hello", 10)
        assert result == "Hello"
    
    def test_truncate_exact_length(self):
        """Should return text as-is when at exact limit."""
        result = truncate_text("Hello", 5)
        assert result == "Hello"
    
    def test_truncate_long_text(self):
        """Should truncate and add suffix when over limit."""
        result = truncate_text("Hello World", 8)
        assert result == "Hello..."
        assert len(result) == 8
    
    def test_truncate_empty_text(self):
        """Should return empty string for empty input."""
        result = truncate_text("", 10)
        assert result == ""
    
    def test_truncate_none_text(self):
        """Should return empty string for None input."""
        result = truncate_text(None, 10)
        assert result == ""
    
    def test_truncate_custom_suffix(self):
        """Should use custom suffix when provided."""
        result = truncate_text("Hello World", 9, suffix="…")
        assert result == "Hello Wo…"


class TestBuildArticleEmbed:
    """Test cases for build_article_embed function."""
    
    def test_build_embed_basic(self):
        """Should build embed with basic fields."""
        article = {
            'title': 'Test Article',
            'link': 'https://example.com/1',
            'description': 'Test description',
            'priority': 'high'
        }
        
        embed = build_article_embed(article, "개발", "💻")
        
        assert embed['url'] == 'https://example.com/1'
        assert embed['color'] == PRIORITY_COLORS['high']
        assert embed['footer']['text'] == "💻 개발"
        assert 'Test Article' in embed['title']
        assert embed['description'] == 'Test description'
    
    def test_build_embed_no_description(self):
        """Should omit description field when empty."""
        article = {
            'title': 'Test Article',
            'link': 'https://example.com/1',
            'description': '',
            'priority': None
        }
        
        embed = build_article_embed(article, "블로그", "📝")
        
        assert 'description' not in embed
    
    def test_build_embed_long_title(self):
        """Should truncate long titles."""
        long_title = "A" * 300
        article = {
            'title': long_title,
            'link': 'https://example.com/1',
            'description': '',
            'priority': None
        }
        
        embed = build_article_embed(article, "개발", "💻")
        
        # Title includes icon prefix, so check total length
        assert len(embed['title']) <= MAX_EMBED_TITLE_LENGTH
    
    def test_build_embed_priority_colors(self):
        """Should apply correct colors for each priority."""
        for priority, expected_color in PRIORITY_COLORS.items():
            article = {
                'title': 'Test',
                'link': 'https://example.com',
                'description': '',
                'priority': priority
            }
            embed = build_article_embed(article, "테스트", "🔧")
            assert embed['color'] == expected_color


class TestChunkEmbeds:
    """Test cases for chunk_embeds function."""
    
    def test_chunk_empty_list(self):
        """Should return empty list for empty input."""
        result = chunk_embeds([])
        assert result == []
    
    def test_chunk_under_limit(self):
        """Should return single chunk when under limit."""
        embeds = [{"title": f"Embed {i}"} for i in range(5)]
        result = chunk_embeds(embeds)
        
        assert len(result) == 1
        assert len(result[0]) == 5
    
    def test_chunk_at_limit(self):
        """Should return single chunk when at exact limit."""
        embeds = [{"title": f"Embed {i}"} for i in range(MAX_EMBEDS_PER_MESSAGE)]
        result = chunk_embeds(embeds)
        
        assert len(result) == 1
        assert len(result[0]) == MAX_EMBEDS_PER_MESSAGE
    
    def test_chunk_over_limit(self):
        """Should split into multiple chunks when over limit."""
        embeds = [{"title": f"Embed {i}"} for i in range(15)]
        result = chunk_embeds(embeds)
        
        assert len(result) == 2
        assert len(result[0]) == 10
        assert len(result[1]) == 5
    
    def test_chunk_custom_limit(self):
        """Should respect custom max_per_chunk."""
        embeds = [{"title": f"Embed {i}"} for i in range(10)]
        result = chunk_embeds(embeds, max_per_chunk=3)
        
        assert len(result) == 4
        assert len(result[0]) == 3
        assert len(result[3]) == 1


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
                {'title': 'Test', 'link': 'https://example.com/1', 'description': 'Summary here', 'published': None, 'priority': 'high', 'category': '개발'},
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verify embed structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'embeds' in payload
        assert len(payload['embeds']) == 1
        assert 'Test' in payload['embeds'][0]['title']
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_failure(self, mock_post, mock_webhook):
        """Should return False on network error."""
        mock_post.side_effect = Exception("Network error")
        
        articles_by_category = {
            "개발": [
                {'title': 'Test', 'link': 'https://example.com/1', 'description': '', 'published': None, 'priority': 'high', 'category': '개발'},
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
        """Should create embeds for multiple categories."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        articles_by_category = {
            "개발": [
                {'title': 'Dev Article', 'link': 'https://example.com/1', 'description': 'Dev summary', 'published': None, 'priority': 'high', 'category': '개발'},
            ],
            "블로그": [
                {'title': 'Blog Post', 'link': 'https://example.com/2', 'description': 'Blog summary', 'published': None, 'priority': None, 'category': '블로그'},
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert len(payload['embeds']) == 2
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_send_notification_chunking(self, mock_post, mock_webhook):
        """Should send multiple requests when over 10 embeds."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        # Create 15 articles (limits now applied per-feed in parser, not here)
        articles_by_category = {
            "개발": [
                {'title': f'Article {i}', 'link': f'https://example.com/{i}', 'description': '', 'published': None, 'priority': 'high', 'category': '개발'}
                for i in range(15)
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        # 15 embeds should be chunked into 2 requests: 10 + 5
        assert mock_post.call_count == 2
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_all_articles_sent_no_category_limit(self, mock_post, mock_webhook):
        """Should send all articles without category limit (limits applied per-feed in parser)."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        # Create 8 articles in one category (all should be sent)
        articles_by_category = {
            "개발": [
                {'title': f'Article {i}', 'link': f'https://example.com/{i}', 'description': '', 'published': None, 'priority': 'high', 'category': '개발'}
                for i in range(8)
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        # All 8 articles should be in embeds (no category limit in notifier)
        assert len(payload['embeds']) == 8
    
    @patch('src.notifier.get_discord_webhook_url', return_value='https://discord.com/webhook')
    @patch('src.notifier.requests.post')
    def test_multiple_categories_chunking(self, mock_post, mock_webhook):
        """Should chunk when total embeds from all categories exceed 10."""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        
        # Create 6 articles in each of 3 categories = 18 total, but limited to 10 per category
        # So we get 6+6+6 = 18 embeds, which should be chunked into 2 requests
        articles_by_category = {
            "개발": [
                {'title': f'Dev {i}', 'link': f'https://example.com/dev/{i}', 'description': '', 'published': None, 'priority': 'high', 'category': '개발'}
                for i in range(6)
            ],
            "블로그": [
                {'title': f'Blog {i}', 'link': f'https://example.com/blog/{i}', 'description': '', 'published': None, 'priority': 'medium', 'category': '블로그'}
                for i in range(6)
            ],
            "뉴스": [
                {'title': f'News {i}', 'link': f'https://example.com/news/{i}', 'description': '', 'published': None, 'priority': 'low', 'category': '뉴스'}
                for i in range(6)
            ]
        }
        
        result = send_discord_notification(articles_by_category)
        
        assert result is True
        # 18 embeds should be split into 2 chunks: 10 + 8
        assert mock_post.call_count == 2
