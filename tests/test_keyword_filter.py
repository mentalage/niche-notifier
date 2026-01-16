"""Tests for keyword filtering functionality."""

import pytest
from src.parser import filter_articles_by_keywords, Article


class TestFilterArticlesByKeywords:
    """Test cases for keyword filtering."""
    
    def setup_method(self):
        """Set up test articles and config."""
        self.articles = [
            {
                "title": "OpenAI releases GPT-5",
                "link": "https://example.com/1",
                "published": None,
                "priority": None,
                "category": None
            },
            {
                "title": "Python 3.12 새로운 기능",
                "link": "https://example.com/2",
                "published": None,
                "priority": None,
                "category": None
            },
            {
                "title": "광고: 특별 할인 행사",
                "link": "https://example.com/3",
                "published": None,
                "priority": None,
                "category": None
            },
            {
                "title": "일상 블로그 포스트",
                "link": "https://example.com/4",
                "published": None,
                "priority": None,
                "category": None
            },
            {
                "title": "AI와 머신러닝의 미래",
                "link": "https://example.com/5",
                "published": None,
                "priority": None,
                "category": None
            },
        ]
        
        self.config = {
            "enabled": True,
            "high_priority": ["AI", "GPT", "ChatGPT"],
            "medium_priority": ["Python", "머신러닝"],
            "low_priority": ["프로그래밍", "개발"],
            "exclude": ["광고", "스폰서"]
        }
    
    def test_high_priority_matching(self):
        """Should match high priority keywords."""
        result = filter_articles_by_keywords(self.articles, self.config)
        
        # Find the GPT article
        gpt_article = next((a for a in result if "GPT" in a["title"]), None)
        assert gpt_article is not None
        assert gpt_article["priority"] == "high"
    
    def test_medium_priority_matching(self):
        """Should match medium priority keywords."""
        result = filter_articles_by_keywords(self.articles, self.config)
        
        # Find the Python article
        python_article = next((a for a in result if "Python" in a["title"]), None)
        assert python_article is not None
        assert python_article["priority"] == "medium"
    
    def test_exclude_keywords(self):
        """Should exclude articles with exclude keywords."""
        result = filter_articles_by_keywords(self.articles, self.config)
        
        # Check that ad article is not in results
        ad_article = next((a for a in result if "광고" in a["title"]), None)
        assert ad_article is None
    
    def test_no_keyword_match_filtered_out(self):
        """Should filter out articles with no keyword match."""
        result = filter_articles_by_keywords(self.articles, self.config)
        
        # "일상 블로그 포스트" has no keywords
        blog_article = next((a for a in result if "일상" in a["title"]), None)
        assert blog_article is None
    
    def test_case_insensitive_matching(self):
        """Should match keywords case-insensitively."""
        articles = [
            {
                "title": "gpt-4 vs gpt-5 comparison",
                "link": "https://example.com/1",
                "published": None,
                "priority": None,
                "category": None
            }
        ]
        
        result = filter_articles_by_keywords(articles, self.config)
        assert len(result) == 1
        assert result[0]["priority"] == "high"
    
    def test_disabled_filtering_returns_all(self):
        """Should return all articles when filtering is disabled."""
        config = {**self.config, "enabled": False}
        result = filter_articles_by_keywords(self.articles, config)
        
        assert len(result) == len(self.articles)
    
    def test_no_keywords_configured_returns_all(self):
        """Should return all articles when no keywords configured."""
        config = {
            "enabled": True,
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "exclude": []
        }
        
        result = filter_articles_by_keywords(self.articles, config)
        assert len(result) == len(self.articles)
    
    def test_priority_precedence(self):
        """Should assign highest matching priority."""
        # Article with both high and medium keywords
        articles = [
            {
                "title": "AI Python 개발",
                "link": "https://example.com/1",
                "published": None,
                "priority": None,
                "category": None
            }
        ]
        
        result = filter_articles_by_keywords(articles, self.config)
        assert len(result) == 1
        # Should be high since AI is checked first
        assert result[0]["priority"] == "high"
    
    def test_exclude_takes_precedence(self):
        """Should exclude article even if it has priority keywords."""
        articles = [
            {
                "title": "광고: AI 특별 할인",
                "link": "https://example.com/1",
                "published": None,
                "priority": None,
                "category": None
            }
        ]
        
        result = filter_articles_by_keywords(articles, self.config)
        assert len(result) == 0
    
    def test_korean_keywords(self):
        """Should match Korean keywords correctly."""
        # Use article that only has medium priority keyword
        articles = [
            {
                "title": "Python과 머신러닝으로 데이터 분석하기",
                "link": "https://example.com/1",
                "published": None,
                "priority": None,
                "category": None
            }
        ]
        
        result = filter_articles_by_keywords(articles, self.config)
        
        # Should match 머신러닝 (medium priority)
        assert len(result) == 1
        assert result[0]["priority"] == "medium"
