"""Tests for the API module."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Should return status ok."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_health_check(self):
        """Should return healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestFeedsAPI:
    """Test feeds API endpoints."""
    
    @patch('api.routers.feeds.get_feeds')
    def test_list_feeds(self, mock_get_feeds):
        """Should return list of feeds."""
        mock_get_feeds.return_value = [
            {"url": "https://example.com/rss", "name": "Test Feed", "category": "개발", "enabled": True}
        ]
        
        response = client.get("/api/feeds")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Test Feed"
    
    @patch('api.routers.feeds.add_feed')
    def test_create_feed_success(self, mock_add_feed):
        """Should create a new feed."""
        mock_add_feed.return_value = True
        
        response = client.post("/api/feeds", json={
            "url": "https://example.com/rss",
            "name": "New Feed",
            "category": "개발",
            "enabled": True
        })
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"]
    
    @patch('api.routers.feeds.add_feed')
    def test_create_feed_failure(self, mock_add_feed):
        """Should return 400 when feed creation fails."""
        mock_add_feed.return_value = False
        
        response = client.post("/api/feeds", json={
            "url": "https://example.com/rss",
            "name": "New Feed",
            "category": "개발"
        })
        
        assert response.status_code == 400
    
    @patch('api.routers.feeds.update_feed')
    def test_update_feed_success(self, mock_update_feed):
        """Should update an existing feed."""
        mock_update_feed.return_value = True
        
        response = client.put(
            "/api/feeds/https%3A%2F%2Fexample.com%2Frss",
            json={"name": "Updated Feed"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.feeds.update_feed')
    def test_update_feed_empty_body(self, mock_update_feed):
        """Should return 400 when no fields to update."""
        response = client.put(
            "/api/feeds/https%3A%2F%2Fexample.com%2Frss",
            json={}
        )
        
        assert response.status_code == 400
    
    @patch('api.routers.feeds.remove_feed')
    def test_delete_feed_success(self, mock_remove_feed):
        """Should delete a feed."""
        mock_remove_feed.return_value = True
        
        response = client.delete("/api/feeds/https%3A%2F%2Fexample.com%2Frss")
        
        assert response.status_code == 200


class TestCategoriesAPI:
    """Test categories API endpoints."""
    
    @patch('api.routers.categories.get_feeds')
    @patch('api.routers.categories.FEED_CATEGORIES', {
        "개발": {"emoji": "💻", "enabled": True},
        "블로그": {"emoji": "📝", "enabled": True}
    })
    def test_list_categories(self, mock_get_feeds):
        """Should return list of categories."""
        mock_get_feeds.return_value = [{"url": "test"}]
        
        response = client.get("/api/categories")
        
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 2


class TestArticlesAPI:
    """Test articles API endpoints."""
    
    @patch('api.routers.articles.get_client')
    def test_list_articles(self, mock_get_client):
        """Should return list of articles."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.order.return_value.range.return_value.execute.return_value.data = [
            {"title": "Test Article", "link": "https://example.com/1", "category": "개발", "priority": "high"}
        ]
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/articles?limit=10")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    @patch('api.routers.articles.get_client')
    def test_generate_preview(self, mock_get_client):
        """Should generate Discord preview."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {"title": "Test Article", "link": "https://example.com/1", "category": "개발", "priority": "high"}
        ]
        mock_get_client.return_value = mock_client
        
        response = client.post("/api/preview", json={"limit": 5})
        
        assert response.status_code == 200
        data = response.json()
        assert "header" in data
        assert "embeds" in data
