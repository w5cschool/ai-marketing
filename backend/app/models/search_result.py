import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SearchResultRaw(Base):
    __tablename__ = "search_results_raw"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("search_tasks.id", ondelete="CASCADE"), index=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    profile_url: Mapped[str] = mapped_column(Text, nullable=False)
    follower_count: Mapped[int | None] = mapped_column(BigInteger)
    email: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    task = relationship("SearchTask", back_populates="raw_results")
    deduped_entries = relationship("SearchResultDeduped", back_populates="raw_result")


class SearchResultDeduped(Base):
    __tablename__ = "search_results_deduped"
    __table_args__ = (UniqueConstraint("task_id", "raw_result_id", name="uq_dedup_task_raw"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("search_tasks.id", ondelete="CASCADE"), index=True)
    raw_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("search_results_raw.id", ondelete="CASCADE"), index=True
    )
    dedup_status: Mapped[str] = mapped_column(
        Enum(
            "unique",
            "duplicate_platform",
            "duplicate_url",
            "duplicate_email",
            "weak_match",
            name="dedup_status",
            create_type=False,
        ),
        nullable=False,
    )
    matched_influencer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("influencers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    task = relationship("SearchTask", back_populates="deduped_results")
    raw_result = relationship("SearchResultRaw", back_populates="deduped_entries")
    matched_influencer = relationship("Influencer")
