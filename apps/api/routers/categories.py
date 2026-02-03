"""Categories API router."""

from fastapi import APIRouter
from typing import List
from apps.api.schemas import CategoryInfo
from src.config import FEED_CATEGORIES
from src.db import get_feeds

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryInfo])
async def list_categories(
    parent: Optional[str] = None,
    include_gics: bool = False
):
    """Get all categories with their info.

    Args:
        parent: Filter by parent category (e.g., "주식/경제" for GICS sectors)
        include_gics: If True, only return GICS sector categories
    """
    categories = []

    for name, config in FEED_CATEGORIES.items():
        # Filter by parent if specified
        if parent is not None:
            if config.get("parent") != parent:
                continue

        # Filter GICS sectors if requested
        if include_gics:
            if not config.get("gics_sector"):
                continue

        # Count feeds in this category from database
        feeds = get_feeds(category=name, enabled_only=False)

        categories.append(CategoryInfo(
            name=name,
            emoji=config.get("emoji", "📂"),
            feed_count=len(feeds),
            enabled=config.get("enabled", True),
            parent=config.get("parent"),
            description=config.get("description"),
            gics_sector=config.get("gics_sector")
        ))

    return categories
