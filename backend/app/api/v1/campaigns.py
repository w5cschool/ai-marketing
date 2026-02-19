import json
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_user_id
from app.config import get_settings
from app.models.email_campaign import EmailCampaign
from app.models.email_draft import EmailDraft
from app.models.email_event import EmailEvent
from app.models.email_message import EmailMessage
from app.models.influencer import Influencer
from app.schemas.campaign import CampaignEventResponse, SendCampaignRequest, SendCampaignResponse
from app.services.email_service import EmailService

router = APIRouter()
settings = get_settings()


@router.post("/campaigns/send", response_model=SendCampaignResponse)
async def send_campaign(
    body: SendCampaignRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> SendCampaignResponse:
    draft = (await db.execute(select(EmailDraft).where(EmailDraft.id == body.draft_id))).scalar_one_or_none()
    if draft is None:
        raise HTTPException(status_code=404, detail="draft not found")

    influencers = (
        await db.execute(
            select(Influencer).where(Influencer.id.in_(body.influencer_ids), Influencer.unsubscribed_at.is_(None))
        )
    ).scalars().all()
    if not influencers:
        raise HTTPException(status_code=400, detail="no valid influencers")

    campaign = EmailCampaign(
        draft_id=draft.id,
        status="sending",
        send_rate_limit=body.send_rate_limit or settings.default_send_rate_limit,
    )
    db.add(campaign)
    await db.flush()

    service = EmailService()
    accepted = await service.send_campaign_messages(
        db=db,
        campaign=campaign,
        influencers=influencers,
        subject=draft.subject,
        body=draft.body,
        user_id=user_id,
    )
    await db.commit()
    return SendCampaignResponse(campaign_id=campaign.id, accepted_count=accepted)


@router.get("/campaigns/{campaign_id}/events", response_model=list[CampaignEventResponse])
async def get_campaign_events(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> list[CampaignEventResponse]:
    rows = (
        await db.execute(
            select(EmailEvent)
            .join(EmailMessage, EmailMessage.id == EmailEvent.message_id)
            .where(EmailMessage.campaign_id == campaign_id)
            .order_by(EmailEvent.occurred_at.asc())
        )
    ).scalars().all()

    return [
        CampaignEventResponse(
            event_id=row.id,
            message_id=row.message_id,
            event_type=row.event_type,
            occurred_at=row.occurred_at,
            raw_payload=row.raw_payload,
        )
        for row in rows
    ]


@router.post("/webhooks/resend")
async def resend_webhook(
    request: Request,
    x_resend_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    payload_bytes = await request.body()
    service = EmailService()

    if not service.verify_webhook_signature(payload_bytes, x_resend_signature, settings.resend_webhook_secret or None):
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = json.loads(payload_bytes.decode("utf-8"))
    saved = await service.process_webhook_event(db, payload)
    await db.commit()
    return {"ok": True, "saved": saved}
