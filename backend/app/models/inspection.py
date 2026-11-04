"""Tabela `inspections`: ajustes da vistoria por sessão e imóvel."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Inspection(Base):
    __tablename__ = "inspections"

    session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    listing_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("listings.id"), primary_key=True
    )
    item_key: Mapped[str] = mapped_column(Text, primary_key=True)
    delta: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (CheckConstraint("delta BETWEEN -10 AND 10", name="delta_range"),)
