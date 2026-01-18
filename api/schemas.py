"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class FeedBase(BaseModel):
    """Base schema for feed data."""
    url: str
    name: Optional[str] = None
    category: str
    enabled: bool = True


class FeedCreate(FeedBase):
    """Schema for creating a new feed."""
    pass


class FeedUpdate(BaseModel):
    """Schema for updating a feed."""
    name: Optional[str] = None
    category: Optional[str] = None
    enabled: Optional[bool] = None


class Feed(FeedBase):
    """Schema for feed response."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CategoryInfo(BaseModel):
    """Schema for category information."""
    name: str
    emoji: str
    feed_count: int
    enabled: bool


class ArticleSummary(BaseModel):
    """Schema for article summary."""
    title: str
    link: str
    category: Optional[str] = None
    priority: Optional[str] = None
    published_at: Optional[datetime] = None


class DiscordEmbed(BaseModel):
    """Schema for Discord embed preview."""
    title: str
    description: Optional[str] = None
    color: int
    url: Optional[str] = None
    footer: Optional[dict] = None


class PreviewRequest(BaseModel):
    """Schema for preview request."""
    category: Optional[str] = None
    limit: int = 5


class PreviewResponse(BaseModel):
    """Schema for preview response."""
    header: str
    embeds: List[DiscordEmbed]
