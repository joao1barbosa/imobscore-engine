"""Tabela `sessions`: uma pessoa, com respostas do onboarding, persona e modo."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    mode: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    price_min: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_max: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    persona_slug: Mapped[str] = mapped_column(Text, ForeignKey("personas.slug"), nullable=False)
    target_pairs: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    participant_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'comparing'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint("mode IN ('product','demo','collection')", name="mode_values"),
        CheckConstraint("purpose IN ('sale','rent')", name="purpose_values"),
        CheckConstraint("price_min < price_max", name="price_min_below_max"),
        CheckConstraint("status IN ('comparing','done')", name="status_values"),
        CheckConstraint(
            "mode <> 'collection' OR (participant_code IS NOT NULL AND consent_at IS NOT NULL)",
            name="collection_requires_consent",
        ),
    )
