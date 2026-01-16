"""Tests for the database module."""

import pytest
from unittest.mock import patch, MagicMock
from src.db import get_processed_links, save_article, filter_new_articles


class TestGetProcessedLinks:
    """Test cases for get_processed_links function."""
    
    @patch('src.db.get_supabase_key', return_value='test-key')
    @patch('src.db.get_supabase_url', return_value='https://test.supabase.co')
    @patch('src.db.get_client')
    def test_returns_set_of_links(self, mock_get_client, mock_url, mock_key):
        """Should return set of processed links."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[
                {'link': 'https://example.com/1'},
                {'link': 'https://example.com/2'},
            ]
        )
        mock_get_client.return_value = mock_client
        
        result = get_processed_links()
        
        assert result == {'https://example.com/1', 'https://example.com/2'}
    
    @patch('src.db.get_supabase_key', return_value='test-key')
    @patch('src.db.get_supabase_url', return_value='https://test.supabase.co')
    @patch('src.db.get_client')
    def test_returns_empty_set_on_error(self, mock_get_client, mock_url, mock_key):
        """Should return empty set on database error."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.execute.side_effect = Exception("DB error")
        mock_get_client.return_value = mock_client
        
        result = get_processed_links()
        
        assert result == set()


class TestSaveArticle:
    """Test cases for save_article function."""
    
    @patch('src.db.get_supabase_key', return_value='test-key')
    @patch('src.db.get_supabase_url', return_value='https://test.supabase.co')
    @patch('src.db.get_client')
    def test_save_article_success(self, mock_get_client, mock_url, mock_key):
        """Should return True on successful save."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        article = {'title': 'Test', 'link': 'https://example.com/1', 'published': None}
        result = save_article(article)
        
        assert result is True
        mock_client.table.return_value.insert.assert_called_once()
    
    @patch('src.db.get_supabase_key', return_value='test-key')
    @patch('src.db.get_supabase_url', return_value='https://test.supabase.co')
    @patch('src.db.get_client')
    def test_save_article_failure(self, mock_get_client, mock_url, mock_key):
        """Should return False on database error."""
        mock_client = MagicMock()
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        mock_get_client.return_value = mock_client
        
        article = {'title': 'Test', 'link': 'https://example.com/1', 'published': None}
        result = save_article(article)
        
        assert result is False


class TestFilterNewArticles:
    """Test cases for filter_new_articles function."""
    
    @patch('src.db.get_processed_links')
    def test_filters_existing_articles(self, mock_get_processed):
        """Should filter out articles that already exist in database."""
        mock_get_processed.return_value = {'https://example.com/old'}
        
        articles = [
            {'title': 'Old Article', 'link': 'https://example.com/old', 'description': '', 'published': None},
            {'title': 'New Article', 'link': 'https://example.com/new', 'description': '', 'published': None},
        ]
        
        result = filter_new_articles(articles)
        
        assert len(result) == 1
        assert result[0]['title'] == 'New Article'
    
    @patch('src.db.get_processed_links')
    def test_returns_all_when_none_processed(self, mock_get_processed):
        """Should return all articles when database is empty."""
        mock_get_processed.return_value = set()
        
        articles = [
            {'title': 'Article 1', 'link': 'https://example.com/1', 'description': '', 'published': None},
            {'title': 'Article 2', 'link': 'https://example.com/2', 'description': '', 'published': None},
        ]
        
        result = filter_new_articles(articles)
        
        assert len(result) == 2
