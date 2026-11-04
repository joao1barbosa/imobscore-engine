"""Tabela `comparisons`: cada par mostrado e a escolha feita."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    listing_a_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("listings.id"), nullable=False
    )
    listing_b_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("listings.id"), nullable=False
    )
    selection: Mapped[str] = mapped_column(Text, nullable=False)
    chosen: Mapped[str | None] = mapped_column(CHAR(1), nullable=True)
    shown_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("session_id", "position"),
        CheckConstraint("selection IN ('adaptive','random')", name="selection_values"),
        CheckConstraint("chosen IN ('A','B')", name="chosen_values"),
        CheckConstraint("listing_a_id <> listing_b_id", name="distinct_listings"),
    )
