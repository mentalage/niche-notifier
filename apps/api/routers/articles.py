"""Articles API router."""

from fastapi import APIRouter, Query
from typing import List, Optional
from apps.api.schemas import ArticleSummary, PreviewRequest, PreviewResponse, DiscordEmbed
from src.db import get_client, TABLE_NAME
from src.config import FEED_CATEGORIES
from src.notifier import (
    build_category_header_embed,
    build_article_embed,
    PRIORITY_COLORS,
    PRIORITY_ICONS,
    CATEGORY_HEADER_COLOR
)

router = APIRouter(tags=["articles"])


@router.get("/articles", response_model=List[ArticleSummary])
async def list_articles(
    category: Optional[str] = None,
    parent: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0
):
    """Get recent articles from database.

    Args:
        category: Filter by specific category (e.g., "정보기술")
        parent: Filter by parent category (e.g., "주식/경제" for all GICS sectors)
        limit: Maximum number of articles to return
        offset: Number of articles to skip
    """
    client = get_client()

    try:
        query = client.table(TABLE_NAME).select("*").order("created_at", desc=True)

        # Handle parent category filtering (e.g., all GICS sectors under "주식/경제")
        if parent:
            child_categories = [
                name for name, config in FEED_CATEGORIES.items()
                if config.get("parent") == parent
            ]
            if child_categories:
                query = query.in_("category", child_categories)
        elif category:
            query = query.eq("category", category)

        query = query.range(offset, offset + limit - 1)
        response = query.execute()

        return [
            ArticleSummary(
                title=row["title"],
                link=row["link"],
                category=row.get("category"),
                subcategory=row.get("subcategory"),  # e.g., GICS sector
                priority=row.get("priority"),
                published_at=row.get("published_at"),
                summary=row.get("summary"),
                summary_status=row.get("summary_status")
            )
            for row in response.data
        ]
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []


@router.post("/preview", response_model=PreviewResponse)
async def generate_preview(request: PreviewRequest):
    """Generate Discord message preview for articles.

    Supports filtering by:
    - category: Specific category (e.g., "정보기술")
    - parent: Parent category to include all subcategories (e.g., "주식/경제")
    """
    client = get_client()

    try:
        # Get recent articles
        query = client.table(TABLE_NAME).select("*").order("created_at", desc=True)

        # Handle parent category filtering
        if hasattr(request, 'parent') and request.parent:
            child_categories = [
                name for name, config in FEED_CATEGORIES.items()
                if config.get("parent") == request.parent
            ]
            if child_categories:
                query = query.in_("category", child_categories)
        elif request.category:
            query = query.eq("category", request.category)

        query = query.limit(request.limit)
        response = query.execute()

        if not response.data:
            return PreviewResponse(
                header="📰 **새로운 기사가 없습니다.**",
                embeds=[]
            )

        # Group by category
        articles_by_category = {}
        for row in response.data:
            cat = row.get("category", "기타")
            if cat not in articles_by_category:
                articles_by_category[cat] = []
            articles_by_category[cat].append({
                "title": row["title"],
                "link": row["link"],
                "description": row.get("summary", ""),  # Use AI summary if available
                "priority": row.get("priority"),
                "category": cat
            })

        # Build embeds
        embeds = []
        total_count = 0
        category_counts = []

        for category_name, articles in articles_by_category.items():
            config = FEED_CATEGORIES.get(category_name, {})
            emoji = config.get("emoji", "📂")

            # Add category header
            header_embed = build_category_header_embed(category_name, emoji, len(articles))
            embeds.append(DiscordEmbed(
                title=header_embed["title"],
                description=header_embed.get("description"),
                color=header_embed["color"]
            ))

            # Add article embeds
            for article in articles:
                priority = article.get("priority")
                color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS[None])
                icon = PRIORITY_ICONS.get(priority, "•")

                embeds.append(DiscordEmbed(
                    title=f"{icon} {article['title'][:100]}",
                    description=article.get("description", "")[:200] if article.get("description") else None,
                    color=color,
                    url=article["link"],
                    footer={"text": f"{emoji} {category_name}"}
                ))

            total_count += len(articles)
            category_counts.append(f"{category_name} {len(articles)}")

        summary = ", ".join(category_counts)
        header = f"📰 **새로운 기사가 도착했습니다!** (총 {total_count}개: {summary})"

        return PreviewResponse(header=header, embeds=embeds)

    except Exception as e:
        print(f"Error generating preview: {e}")
        return PreviewResponse(
            header="⚠️ **미리보기 생성 실패**",
            embeds=[]
        )
