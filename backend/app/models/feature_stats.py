"""Tabela `feature_stats`: centro e escala de cada característica, por segmento."""

from sqlalchemy import CheckConstraint, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FeatureStat(Base):
    __tablename__ = "feature_stats"

    city: Mapped[str] = mapped_column(Text, primary_key=True)
    purpose: Mapped[str] = mapped_column(Text, primary_key=True)
    feature_key: Mapped[str] = mapped_column(Text, primary_key=True)
    center: Mapped[float] = mapped_column(Float, nullable=False)
    scale: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (CheckConstraint("scale > 0", name="scale_positive"),)
