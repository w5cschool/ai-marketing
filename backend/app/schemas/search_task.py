import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SearchTaskCreate(BaseModel):
    query: str = Field(min_length=1)
    platforms: list[str] = Field(default_factory=lambda: ["youtube"])
    region: str | None = None
    follower_min: int | None = Field(default=None, ge=0)
    follower_max: int | None = Field(default=None, ge=0)


class SearchTaskCreateResponse(BaseModel):
    task_id: uuid.UUID
    status: str


class SearchTaskStatusResponse(BaseModel):
    task_id: uuid.UUID
    status: str
    result_count: int
    created_at: datetime
    updated_at: datetime


class SearchTaskListItem(BaseModel):
    task_id: uuid.UUID
    query_raw: str
    status: str
    result_count: int
    created_at: datetime
    updated_at: datetime


class SearchResultResponse(BaseModel):
    deduped_id: uuid.UUID
    raw_result_id: uuid.UUID
    dedup_status: str
    matched_influencer_id: uuid.UUID | None
    platform: str
    platform_user_id: str
    display_name: str
    profile_url: str
    follower_count: int | None
    email: str | None
