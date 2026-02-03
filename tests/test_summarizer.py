"""Tests for AI Summarizer module."""

import pytest
from unittest.mock import MagicMock, patch

from src.summarizer import (
    extract_content_jina,
    generate_summary_gemini,
    build_summary_prompt,
    ArticleSummarizer,
)


class TestContentExtraction:
    """Test content extraction from URLs."""

    def test_extract_content_jina_success(self):
        """Test successful content extraction with jina.ai."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Test article content here"

        with patch("requests.get", return_value=mock_response):
            result = extract_content_jina("https://example.com/article")

            assert result == "Test article content here"

    def test_extract_content_jina_failure(self):
        """Test content extraction failure."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("requests.get", return_value=mock_response):
            result = extract_content_jina("https://example.com/article")

            assert result is None

    def test_extract_content_jina_long_content_truncation(self):
        """Test that long content is truncated to 15000 chars."""
        long_content = "x" * 20000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = long_content

        with patch("requests.get", return_value=mock_response):
            result = extract_content_jina("https://example.com/article")

            assert len(result) == 15000


class TestSummaryPrompt:
    """Test summary prompt building."""

    def test_build_summary_prompt_basic(self):
        """Test basic prompt building."""
        title = "Test Article"
        content = "Test content here"

        prompt = build_summary_prompt(title, content)

        assert "Test Article" in prompt
        assert "Test content here" in prompt
        assert "한국어" in prompt or "Korean" in prompt
        assert "2-3 sentence" in prompt or "2-3문장" in prompt

    def test_build_summary_prompt_empty_content(self):
        """Test prompt with empty content."""
        title = "Test Article"
        content = ""

        prompt = build_summary_prompt(title, content)

        assert "Test Article" in prompt


class TestGeminiAPI:
    """Test Gemini API integration."""

    def test_generate_summary_success(self):
        """Test successful summary generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "This is a test summary of the article."}
                        ]
                    }
                }
            ]
        }

        with patch("requests.post", return_value=mock_response):
            with patch("src.summarizer.get_gemini_api_key", return_value="test-key"):
                result = generate_summary_gemini("Test Title", "Test content")

                assert result == "This is a test summary of the article."

    def test_generate_summary_no_api_key(self):
        """Test summary generation fails without API key."""
        with patch("src.summarizer.get_gemini_api_key", return_value=""):
            result = generate_summary_gemini("Test Title", "Test content")

            assert result is None

    def test_generate_summary_api_error(self):
        """Test summary generation handles API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch("requests.post", return_value=mock_response):
            with patch("src.summarizer.get_gemini_api_key", return_value="test-key"):
                result = generate_summary_gemini("Test Title", "Test content")

                assert result is None

    def test_generate_summary_truncates_long_summary(self):
        """Test that long summaries are truncated."""
        long_summary = "x" * 400
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": long_summary}
                        ]
                    }
                }
            ]
        }

        with patch("requests.post", return_value=mock_response):
            with patch("src.summarizer.get_gemini_api_key", return_value="test-key"):
                result = generate_summary_gemini("Test Title", "Test content")

                assert len(result) == 300
                assert result.endswith("...")


class TestArticleSummarizer:
    """Test ArticleSummarizer class."""

    def test_summarize_article_with_content_extraction(self):
        """Test summarizing an article with content extraction."""
        mock_extract = MagicMock(return_value="Extracted article content")
        mock_generate = MagicMock(return_value="AI-generated summary")

        with patch("src.summarizer.extract_article_content", mock_extract):
            with patch("src.summarizer.generate_summary_gemini", mock_generate):
                with patch("src.summarizer.get_gemini_api_key", return_value="test-key"):
                    summarizer = ArticleSummarizer()
                    result = summarizer.summarize_article(
                        "Test Title",
                        "https://example.com/article",
                        "Description"
                    )

                    assert result == "AI-generated summary"
                    mock_extract.assert_called_once_with("https://example.com/article")
                    mock_generate.assert_called_once()

    def test_summarize_article_falls_back_to_description(self):
        """Test that summarizer falls back to description when extraction fails."""
        mock_extract = MagicMock(return_value=None)
        mock_generate = MagicMock(return_value="AI-generated summary")

        with patch("src.summarizer.extract_article_content", mock_extract):
            with patch("src.summarizer.generate_summary_gemini", mock_generate):
                with patch("src.summarizer.get_gemini_api_key", return_value="test-key"):
                    summarizer = ArticleSummarizer()
                    result = summarizer.summarize_article(
                        "Test Title",
                        "https://example.com/article",
                        "Fallback description"
                    )

                    assert result == "AI-generated summary"
                    # Should use description as content
                    mock_generate.assert_called_once_with("Test Title", "Fallback description")

    def test_summarize_article_no_api_key(self):
        """Test that summarizer returns None without API key."""
        with patch("src.summarizer.get_gemini_api_key", return_value=""):
            summarizer = ArticleSummarizer()
            result = summarizer.summarize_article(
                "Test Title",
                "https://example.com/article",
                "Description"
            )

            assert result is None

    def test_summarize_batch(self):
        """Test batch summarization."""
        articles = [
            {"title": f"Article {i}", "link": f"https://example.com/{i}", "description": f"Desc {i}"}
            for i in range(3)
        ]

        def mock_summarize(self, title, url, description):
            return f"Summary for {title}"

        with patch.object(ArticleSummarizer, "summarize_article", mock_summarize):
            with patch("src.summarizer.get_gemini_api_key", return_value="test-key"):
                summarizer = ArticleSummarizer()
                results = summarizer.summarize_batch(articles)

                assert len(results) == 3
                for i in range(3):
                    assert f"https://example.com/{i}" in results
                    assert results[f"https://example.com/{i}"] == f"Summary for Article {i}"


def test_summarize_article_convenience_function():
    """Test the convenience function for single article summarization."""
    with patch("src.summarizer.ArticleSummarizer.summarize_article", return_value="Test summary"):
        from src.summarizer import summarize_article

        result = summarize_article("Title", "https://example.com", "Desc")

        assert result == "Test summary"


def test_summarize_articles_batch_convenience_function():
    """Test the convenience function for batch summarization."""
    articles = [{"title": "Test", "link": "https://example.com", "description": "Desc"}]

    with patch("src.summarizer.ArticleSummarizer.summarize_batch", return_value={"https://example.com": "Summary"}):
        from src.summarizer import summarize_articles_batch

        result = summarize_articles_batch(articles)

        assert result == {"https://example.com": "Summary"}
