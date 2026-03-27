"""Brief service — daily intelligence brief generation.

AI drafts findings from recent data. This is a bounded agent job:
retrieval -> structured evidence pack -> analysis -> human review.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.alert import Alert
from app.models.entity import Entity


async def generate_daily_brief(db: AsyncSession, hours: int = 24) -> dict:
    """Generate a structured daily intelligence brief.

    Returns a structured brief with sections, not free-form text.
    Every statement traces back to evidence.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Gather recent content stats
    content_count = (
        await db.execute(
            select(func.count(Content.id)).where(Content.collected_at >= cutoff)
        )
    ).scalar() or 0

    platform_breakdown = (
        await db.execute(
            select(Content.platform, func.count(Content.id))
            .where(Content.collected_at >= cutoff)
            .group_by(Content.platform)
        )
    ).all()

    # Top risk content
    high_risk = (
        await db.execute(
            select(Content)
            .where(and_(Content.collected_at >= cutoff, Content.risk_score > 0.5))
            .order_by(Content.risk_score.desc())
            .limit(10)
        )
    ).scalars().all()

    # Recent alerts
    recent_alerts = (
        await db.execute(
            select(Alert)
            .where(Alert.created_at >= cutoff)
            .order_by(Alert.created_at.desc())
            .limit(20)
        )
    ).scalars().all()

    # New alerts by status
    alert_stats = (
        await db.execute(
            select(Alert.status, func.count(Alert.id))
            .where(Alert.created_at >= cutoff)
            .group_by(Alert.status)
        )
    ).all()

    # Top mentioned entities
    # (In Phase 2 this becomes a real entity co-occurrence analysis)

    brief = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_hours": hours,
        "period_start": cutoff.isoformat(),
        "summary": {
            "total_content_items": content_count,
            "platform_breakdown": {p: c for p, c in platform_breakdown if p},
            "alert_summary": {s: c for s, c in alert_stats},
        },
        "high_risk_content": [
            {
                "id": str(c.id),
                "platform": c.platform,
                "text_preview": (c.text or "")[:200],
                "risk_score": c.risk_score,
                "risk_labels": c.risk_labels,
                "source_url": c.source_url,
                "observed_at": c.observed_at.isoformat() if c.observed_at else None,
            }
            for c in high_risk
        ],
        "recent_alerts": [
            {
                "id": str(a.id),
                "type": a.alert_type,
                "title": a.title,
                "priority": a.priority,
                "status": a.status,
                "created_at": a.created_at.isoformat(),
            }
            for a in recent_alerts
        ],
        "action_items": [],
        "provenance": {
            "data_sources": list({p for p, _ in platform_breakdown if p}),
            "generation_method": "structured_aggregation_v1",
            "note": "All items linked to source evidence. No LLM summarization in MVP.",
        },
    }

    return brief
