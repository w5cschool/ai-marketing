import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EmailEvent(Base):
    __tablename__ = "email_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("email_messages.id", ondelete="CASCADE"), index=True
    )
    provider_event_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    event_type: Mapped[str] = mapped_column(
        Enum("delivered", "bounced", "opened", "replied", "unsubscribed", "unknown", name="email_event_type", create_type=False),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
