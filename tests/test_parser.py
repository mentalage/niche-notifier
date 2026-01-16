"""Tests for the RSS parser module."""

import pytest
from unittest.mock import patch, MagicMock
from src.parser import parse_feed, parse_all_feeds, Article


class TestParseFeed:
    """Test cases for parse_feed function."""
    
    @patch('src.parser.feedparser.parse')
    def test_parse_feed_returns_articles(self, mock_parse):
        """Should return list of articles from feed."""
        mock_parse.return_value = MagicMock(
            entries=[
                {'title': 'Test Article 1', 'link': 'https://example.com/1', 'published': '2024-01-01'},
                {'title': 'Test Article 2', 'link': 'https://example.com/2', 'published': '2024-01-02'},
            ]
        )
        
        result = parse_feed('https://example.com/feed')
        
        assert len(result) == 2
        assert result[0]['title'] == 'Test Article 1'
        assert result[0]['link'] == 'https://example.com/1'
        assert result[0]['description'] == ''
        assert result[0]['priority'] is None
        assert result[0]['category'] is None
        assert result[1]['title'] == 'Test Article 2'
        assert result[1]['description'] == ''
        assert result[1]['priority'] is None
        assert result[1]['category'] is None
    
    @patch('src.parser.feedparser.parse')
    def test_parse_feed_skips_entries_without_link(self, mock_parse):
        """Should skip entries that don't have a link."""
        mock_parse.return_value = MagicMock(
            entries=[
                {'title': 'Has Link', 'link': 'https://example.com/1'},
                {'title': 'No Link', 'link': ''},
                {'title': 'Also No Link'},
            ]
        )
        
        result = parse_feed('https://example.com/feed')
        
        assert len(result) == 1
        assert result[0]['title'] == 'Has Link'
        assert result[0]['description'] == ''
        assert result[0]['priority'] is None
        assert result[0]['category'] is None
    
    @patch('src.parser.feedparser.parse')
    def test_parse_feed_handles_missing_title(self, mock_parse):
        """Should use 'Untitled' for entries without title."""
        mock_parse.return_value = MagicMock(
            entries=[
                {'link': 'https://example.com/1'},
            ]
        )
        
        result = parse_feed('https://example.com/feed')
        
        assert result[0]['title'] == 'Untitled'
        assert result[0]['description'] == ''
        assert result[0]['priority'] is None
        assert result[0]['category'] is None

    @patch('src.parser.feedparser.parse')
    def test_parse_feed_extracts_description_and_cleans_html(self, mock_parse):
        """Should extract description and strip HTML tags."""
        mock_parse.return_value = MagicMock(
            entries=[
                {
                    'title': 'HTML Article', 
                    'link': 'https://example.com/html', 
                    'summary': '<p>Hello <b>World</b></p><br/>'
                },
            ]
        )
        
        result = parse_feed('https://example.com/feed')
        
        assert len(result) == 1
        assert result[0]['description'] == 'Hello World'


class TestParseAllFeeds:
    """Test cases for parse_all_feeds function."""
    
    @patch('src.parser.parse_feed')
    def test_parse_all_feeds_combines_results(self, mock_parse_feed):
        """Should combine articles from all feeds."""
        mock_parse_feed.side_effect = [
            [{'title': 'Feed 1 Article', 'link': 'https://feed1.com/1', 'description': '', 'published': None, 'priority': None, 'category': None}],
            [{'title': 'Feed 2 Article', 'link': 'https://feed2.com/1', 'description': '', 'published': None, 'priority': None, 'category': None}],
        ]
        
        result = parse_all_feeds(['https://feed1.com', 'https://feed2.com'])
        
        assert len(result) == 2
        assert result[0]['title'] == 'Feed 1 Article'
        assert result[1]['title'] == 'Feed 2 Article'
    
    @patch('src.parser.parse_feed')
    def test_parse_all_feeds_handles_empty_feeds(self, mock_parse_feed):
        """Should handle feeds that return no articles."""
        mock_parse_feed.side_effect = [
            [],
            [{'title': 'Only Article', 'link': 'https://feed.com/1', 'description': '', 'published': None, 'priority': None, 'category': None}],
        ]
        
        result = parse_all_feeds(['https://empty.com', 'https://feed.com'])
        
        assert len(result) == 1
