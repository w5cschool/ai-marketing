import uuid

from pydantic import BaseModel, Field


class SaveInfluencersRequest(BaseModel):
    task_id: uuid.UUID
    selected_result_ids: list[uuid.UUID] = Field(default_factory=list)


class SaveInfluencersResponse(BaseModel):
    saved_count: int
    skipped_count: int


class InfluencerListItem(BaseModel):
    id: uuid.UUID
    platform: str
    platform_user_id: str
    display_name: str
    profile_url: str
    follower_count: int | None
    email: str | None
    saved_by: str
