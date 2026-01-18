"""Tests for config module - YAML loading functionality."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch

from src.config import load_feed_categories, DEFAULT_FEED_CATEGORIES, FEEDS_CONFIG_PATH


class TestLoadFeedCategories:
    """Test load_feed_categories function."""
    
    def test_load_from_yaml_file(self, tmp_path):
        """Test loading categories from a valid YAML file."""
        yaml_content = {
            "테스트": {
                "enabled": True,
                "emoji": "🧪",
                "feeds": [{"url": "https://example.com/feed", "name": "Test Feed"}],
                "keyword_filters": {"enabled": False}
            }
        }
        
        yaml_file = tmp_path / "feeds.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, allow_unicode=True)
        
        result = load_feed_categories(yaml_file)
        
        assert "테스트" in result
        assert result["테스트"]["emoji"] == "🧪"
        assert result["테스트"]["enabled"] is True
        assert len(result["테스트"]["feeds"]) == 1
        assert result["테스트"]["feeds"][0]["name"] == "Test Feed"
    
    def test_fallback_to_defaults_when_file_missing(self, tmp_path):
        """Test fallback to DEFAULT_FEED_CATEGORIES when file doesn't exist."""
        nonexistent_path = tmp_path / "nonexistent" / "feeds.yaml"
        
        result = load_feed_categories(nonexistent_path)
        
        assert result == DEFAULT_FEED_CATEGORIES
    
    def test_fallback_on_invalid_yaml(self, tmp_path):
        """Test fallback when YAML file is invalid."""
        yaml_file = tmp_path / "feeds.yaml"
        yaml_file.write_text("invalid: yaml: content: [", encoding="utf-8")
        
        result = load_feed_categories(yaml_file)
        
        assert result == DEFAULT_FEED_CATEGORIES
    
    def test_fallback_on_empty_yaml(self, tmp_path):
        """Test fallback when YAML file is empty."""
        yaml_file = tmp_path / "feeds.yaml"
        yaml_file.write_text("", encoding="utf-8")
        
        result = load_feed_categories(yaml_file)
        
        assert result == DEFAULT_FEED_CATEGORIES
    
    def test_preserves_korean_characters(self, tmp_path):
        """Test that Korean characters are preserved correctly."""
        yaml_content = {
            "개발": {
                "enabled": True,
                "emoji": "💻",
                "feeds": [{"url": "https://example.com", "name": "한글 피드"}],
                "keyword_filters": {
                    "enabled": True,
                    "high_priority": ["인공지능", "딥러닝"],
                    "exclude": ["광고"]
                }
            }
        }
        
        yaml_file = tmp_path / "feeds.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, allow_unicode=True)
        
        result = load_feed_categories(yaml_file)
        
        assert "개발" in result
        assert result["개발"]["feeds"][0]["name"] == "한글 피드"
        assert "인공지능" in result["개발"]["keyword_filters"]["high_priority"]


class TestDefaultFeedCategories:
    """Test DEFAULT_FEED_CATEGORIES structure."""
    
    def test_has_required_categories(self):
        """Test that default config has expected categories."""
        assert "개발" in DEFAULT_FEED_CATEGORIES
        assert "주식/경제" in DEFAULT_FEED_CATEGORIES
    
    def test_category_has_required_fields(self):
        """Test that each category has required fields."""
        for category_name, config in DEFAULT_FEED_CATEGORIES.items():
            assert "enabled" in config, f"{category_name} missing 'enabled'"
            assert "emoji" in config, f"{category_name} missing 'emoji'"
            assert "feeds" in config, f"{category_name} missing 'feeds'"
    
    def test_feeds_have_url_and_name(self):
        """Test that feeds in default config have url and name."""
        for category_name, config in DEFAULT_FEED_CATEGORIES.items():
            for feed in config.get("feeds", []):
                if isinstance(feed, dict):
                    assert "url" in feed, f"Feed in {category_name} missing 'url'"


class TestFeedsConfigPath:
    """Test FEEDS_CONFIG_PATH constant."""
    
    def test_points_to_project_root(self):
        """Test that config path points to project root."""
        # FEEDS_CONFIG_PATH should be at project root level
        assert FEEDS_CONFIG_PATH.name == "feeds.yaml"
        assert FEEDS_CONFIG_PATH.parent.name == "notify-niche"
