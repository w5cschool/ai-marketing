from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_user_id
from app.models.audit_log import AuditLog
from app.models.influencer import Influencer
from app.models.search_result import SearchResultRaw
from app.schemas.influencer import InfluencerListItem, SaveInfluencersRequest, SaveInfluencersResponse

router = APIRouter()


@router.get("/influencers", response_model=list[InfluencerListItem])
async def list_influencers(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> list[InfluencerListItem]:
    influencers = (
        await db.execute(
            select(Influencer)
            .where(Influencer.saved_by == user_id)
            .order_by(Influencer.saved_at.desc())
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()

    return [
        InfluencerListItem(
            id=item.id,
            platform=item.platform,
            platform_user_id=item.platform_user_id,
            display_name=item.display_name,
            profile_url=item.profile_url,
            follower_count=item.follower_count,
            email=item.email,
            saved_by=item.saved_by,
        )
        for item in influencers
    ]


@router.post("/influencers/save", response_model=SaveInfluencersResponse)
async def save_influencers(
    body: SaveInfluencersRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> SaveInfluencersResponse:
    raw_rows = (
        await db.execute(
            select(SearchResultRaw).where(SearchResultRaw.id.in_(body.selected_result_ids), SearchResultRaw.task_id == body.task_id)
        )
    ).scalars().all()

    saved_count = 0
    skipped_count = 0

    for raw in raw_rows:
        exists = (
            await db.execute(
                select(Influencer).where(
                    Influencer.platform == raw.platform,
                    Influencer.platform_user_id == raw.platform_user_id,
                )
            )
        ).scalar_one_or_none()
        if exists:
            skipped_count += 1
            continue

        influencer = Influencer(
            platform=raw.platform,
            platform_user_id=raw.platform_user_id,
            display_name=raw.display_name,
            profile_url=raw.profile_url,
            follower_count=raw.follower_count,
            email=raw.email,
            saved_by=user_id,
        )
        db.add(influencer)
        await db.flush()

        db.add(
            AuditLog(
                user_id=user_id,
                action="influencer_saved",
                entity_type="influencer",
                entity_id=influencer.id,
                detail={"task_id": str(body.task_id)},
            )
        )
        saved_count += 1

    await db.commit()
    return SaveInfluencersResponse(saved_count=saved_count, skipped_count=skipped_count)
