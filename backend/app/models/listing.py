"""Tabela `listings`: os imóveis simulados do catálogo e seus atributos brutos."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Numeric,
    SmallInteger,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    neighborhood: Mapped[str] = mapped_column(Text, nullable=False)
    price_brl: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    area_m2: Mapped[Decimal] = mapped_column(Numeric(7, 1), nullable=False)
    bedrooms: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    bathrooms: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    parking: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dist_center_km: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    age_years: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    leisure_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    pet_friendly: Mapped[bool] = mapped_column(Boolean, nullable=False)
    doorman_24h: Mapped[bool] = mapped_column(Boolean, nullable=False)
    illustration: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint("purpose IN ('sale','rent')", name="purpose_values"),
        CheckConstraint("kind IN ('apartment','house')", name="kind_values"),
        CheckConstraint("price_brl > 0", name="price_positive"),
        CheckConstraint("area_m2 > 0", name="area_positive"),
        CheckConstraint("bedrooms BETWEEN 1 AND 6", name="bedrooms_range"),
        CheckConstraint("bathrooms BETWEEN 1 AND 6", name="bathrooms_range"),
        CheckConstraint("parking BETWEEN 0 AND 4", name="parking_range"),
        CheckConstraint("dist_center_km >= 0", name="dist_center_non_negative"),
        CheckConstraint("age_years BETWEEN 0 AND 60", name="age_years_range"),
        CheckConstraint("leisure_count BETWEEN 0 AND 3", name="leisure_count_range"),
        Index("ix_listings_segment", "city", "purpose", "price_brl"),
    )
