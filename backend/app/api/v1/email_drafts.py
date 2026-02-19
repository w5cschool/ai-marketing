from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.email_draft import EmailDraft
from app.models.influencer import Influencer
from app.schemas.email_draft import EmailDraftResponse, GenerateEmailDraftRequest
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/email-drafts/generate", response_model=EmailDraftResponse)
async def generate_email_draft(body: GenerateEmailDraftRequest, db: AsyncSession = Depends(get_db)) -> EmailDraftResponse:
    influencers = (
        await db.execute(select(Influencer).where(Influencer.id.in_(body.influencer_ids)))
    ).scalars().all()
    if not influencers:
        raise HTTPException(status_code=400, detail="no influencers found")

    context = {
        "influencers": [
            {
                "id": str(i.id),
                "name": i.display_name,
                "platform": i.platform,
                "followers": i.follower_count,
            }
            for i in influencers
        ]
    }

    ai = AIService()
    generated = await ai.generate_email_draft(body.goal, body.tone, body.language, context=context)

    draft = EmailDraft(
        goal=body.goal,
        tone=body.tone,
        language=body.language,
        subject=generated["subject"],
        body=generated["body"],
        variables=generated.get("variables", {}),
        influencer_ids=body.influencer_ids,
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return EmailDraftResponse(
        id=draft.id,
        subject=draft.subject,
        body=draft.body,
        variables=draft.variables,
        created_at=draft.created_at,
    )
