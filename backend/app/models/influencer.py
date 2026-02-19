import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Influencer(Base):
    __tablename__ = "influencers"
    __table_args__ = (UniqueConstraint("platform", "platform_user_id", name="uq_influencers_platform_user"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    profile_url: Mapped[str] = mapped_column(Text, nullable=False)
    follower_count: Mapped[int | None] = mapped_column(BigInteger)
    email: Mapped[str | None] = mapped_column(Text, index=True)
    saved_by: Mapped[str] = mapped_column(Text, nullable=False)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    unsubscribed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
