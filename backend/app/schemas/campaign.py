import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SendCampaignRequest(BaseModel):
    draft_id: uuid.UUID
    influencer_ids: list[uuid.UUID] = Field(default_factory=list)
    send_rate_limit: int | None = Field(default=None, ge=1)


class SendCampaignResponse(BaseModel):
    campaign_id: uuid.UUID
    accepted_count: int


class CampaignEventResponse(BaseModel):
    event_id: uuid.UUID
    message_id: uuid.UUID
    event_type: str
    occurred_at: datetime
    raw_payload: dict
