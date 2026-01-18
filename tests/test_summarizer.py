"""Tests for the Summarizer module."""

import pytest
from unittest.mock import patch, MagicMock


class TestExtractArticleContent:
    """Test article content extraction."""
    
    @patch('src.summarizer.trafilatura.fetch_url')
    @patch('src.summarizer.trafilatura.extract')
    def test_extract_content_success(self, mock_extract, mock_fetch):
        """Should extract content from URL."""
        from src.summarizer import extract_article_content
        
        mock_fetch.return_value = "<html>test content</html>"
        mock_extract.return_value = "Extracted article content"
        
        result = extract_article_content("https://example.com/article")
        
        assert result == "Extracted article content"
        mock_fetch.assert_called_once_with("https://example.com/article")
    
    @patch('src.summarizer.trafilatura.fetch_url')
    def test_extract_content_fetch_failure(self, mock_fetch):
        """Should return None when fetch fails."""
        from src.summarizer import extract_article_content
        
        mock_fetch.return_value = None
        
        result = extract_article_content("https://example.com/article")
        
        assert result is None
    
    @patch('src.summarizer.trafilatura.fetch_url')
    def test_extract_content_exception(self, mock_fetch):
        """Should return None when exception occurs."""
        from src.summarizer import extract_article_content
        
        mock_fetch.side_effect = Exception("Network error")
        
        result = extract_article_content("https://example.com/article")
        
        assert result is None


class TestSummarizeWithGemini:
    """Test Gemini summarization."""
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('src.summarizer.genai')
    def test_summarize_success(self, mock_genai):
        """Should generate summary with Gemini."""
        from src.summarizer import summarize_with_gemini
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "  This is a summary.  "
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        result = summarize_with_gemini("Article content here", "Test Title")
        
        assert result == "This is a summary."
        mock_client.models.generate_content.assert_called_once()
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('src.summarizer.genai')
    def test_summarize_exception(self, mock_genai):
        """Should return None when exception occurs."""
        from src.summarizer import summarize_with_gemini
        
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API error")
        mock_genai.Client.return_value = mock_client
        
        result = summarize_with_gemini("Article content", "Test Title")
        
        assert result is None


class TestSummarizeArticle:
    """Test combined summarize_article function."""
    
    @patch('src.summarizer.summarize_with_gemini')
    @patch('src.summarizer.extract_article_content')
    def test_summarize_article_success(self, mock_extract, mock_summarize):
        """Should extract and summarize article."""
        from src.summarizer import summarize_article
        
        mock_extract.return_value = "Article content"
        mock_summarize.return_value = "Summary text"
        
        result = summarize_article("https://example.com/article", "Test Title")
        
        assert result == "Summary text"
        mock_extract.assert_called_once_with("https://example.com/article")
        mock_summarize.assert_called_once_with("Article content", "Test Title")
    
    @patch('src.summarizer.extract_article_content')
    def test_summarize_article_no_content(self, mock_extract):
        """Should return None when content extraction fails."""
        from src.summarizer import summarize_article
        
        mock_extract.return_value = None
        
        result = summarize_article("https://example.com/article", "Test Title")
        
        assert result is None


class TestSummarizeArticles:
    """Test batch summarization."""
    
    @patch('src.summarizer.summarize_article')
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    def test_summarize_articles_batch(self, mock_summarize):
        """Should summarize multiple articles."""
        from src.summarizer import summarize_articles
        
        mock_summarize.side_effect = ["Summary 1", "Summary 2", None]
        
        articles = [
            {"title": "Article 1", "link": "https://example.com/1", "summary": None},
            {"title": "Article 2", "link": "https://example.com/2", "summary": None},
            {"title": "Article 3", "link": "https://example.com/3", "summary": None},
        ]
        
        result = summarize_articles(articles)
        
        assert result[0]["summary"] == "Summary 1"
        assert result[1]["summary"] == "Summary 2"
        assert result[2]["summary"] is None
    
    @patch.dict('os.environ', {}, clear=True)
    def test_summarize_articles_no_api_key(self):
        """Should skip summarization when API key is not set."""
        from src.summarizer import summarize_articles
        
        articles = [{"title": "Test", "link": "https://example.com", "summary": None}]
        
        result = summarize_articles(articles)
        
        # Should return articles unchanged
        assert result[0]["summary"] is None
    
    @patch('src.summarizer.summarize_article')
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    def test_summarize_articles_with_limit(self, mock_summarize):
        """Should respect max_articles limit."""
        from src.summarizer import summarize_articles
        
        mock_summarize.return_value = "Summary"
        
        articles = [
            {"title": f"Article {i}", "link": f"https://example.com/{i}", "summary": None}
            for i in range(5)
        ]
        
        summarize_articles(articles, max_articles=2)
        
        # Should only call summarize for first 2 articles
        assert mock_summarize.call_count == 2
