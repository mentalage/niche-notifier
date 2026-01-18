"""Categories API router."""

from fastapi import APIRouter
from typing import List
from apps.api.schemas import CategoryInfo
from src.config import FEED_CATEGORIES
from src.db import get_feeds

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryInfo])
async def list_categories():
    """Get all categories with their info."""
    categories = []
    
    for name, config in FEED_CATEGORIES.items():
        # Count feeds in this category from database
        feeds = get_feeds(category=name, enabled_only=False)
        
        categories.append(CategoryInfo(
            name=name,
            emoji=config.get("emoji", "📂"),
            feed_count=len(feeds),
            enabled=config.get("enabled", True)
        ))
    
    return categories
