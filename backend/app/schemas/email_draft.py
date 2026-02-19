import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GenerateEmailDraftRequest(BaseModel):
    goal: str = Field(min_length=1)
    tone: str = Field(default="professional")
    language: str = Field(default="en")
    influencer_ids: list[uuid.UUID] = Field(default_factory=list)


class EmailDraftResponse(BaseModel):
    id: uuid.UUID
    subject: str
    body: str
    variables: dict
    created_at: datetime
