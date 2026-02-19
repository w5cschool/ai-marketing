import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SearchTask(Base):
    __tablename__ = "search_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    query_raw: Mapped[str] = mapped_column(Text, nullable=False)
    query_parsed: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "done", "failed", name="search_status", create_type=False),
        nullable=False,
        default="pending",
    )
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    raw_results = relationship("SearchResultRaw", back_populates="task", cascade="all, delete-orphan")
    deduped_results = relationship("SearchResultDeduped", back_populates="task", cascade="all, delete-orphan")
