"""Feeds API router."""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from apps.api.schemas import Feed, FeedCreate, FeedUpdate
from src.db import get_feeds, add_feed, update_feed, remove_feed, get_client, FEEDS_TABLE

router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.get("", response_model=List[Feed])
async def list_feeds(
    category: Optional[str] = None,
    enabled_only: bool = False
):
    """Get all RSS feeds, optionally filtered by category."""
    feeds = get_feeds(category=category, enabled_only=enabled_only)
    return feeds


@router.post("", response_model=dict)
async def create_feed(feed: FeedCreate):
    """Add a new RSS feed."""
    success = add_feed(url=feed.url, category=feed.category, name=feed.name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add feed. URL may already exist.")
    return {"message": "Feed added successfully", "url": feed.url}


@router.put("/{feed_url:path}", response_model=dict)
async def modify_feed(feed_url: str, updates: FeedUpdate):
    """Update an existing RSS feed."""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    success = update_feed(url=feed_url, updates=update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Feed not found or update failed")
    return {"message": "Feed updated successfully", "url": feed_url}


@router.delete("/{feed_url:path}", response_model=dict)
async def delete_feed(feed_url: str):
    """Remove a RSS feed."""
    success = remove_feed(url=feed_url)
    if not success:
        raise HTTPException(status_code=404, detail="Feed not found or deletion failed")
    return {"message": "Feed deleted successfully", "url": feed_url}
