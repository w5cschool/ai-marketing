import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmailCampaign(Base):
    __tablename__ = "email_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_drafts.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(
        Enum("draft", "sending", "done", "failed", name="campaign_status", create_type=False),
        nullable=False,
        default="draft",
    )
    send_rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    accepted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    draft = relationship("EmailDraft")
    messages = relationship("EmailMessage", back_populates="campaign", cascade="all, delete-orphan")
