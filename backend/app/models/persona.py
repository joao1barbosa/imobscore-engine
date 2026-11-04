"""Tabela `personas`: as três personas com média e desvio da priori."""

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Persona(Base):
    __tablename__ = "personas"

    slug: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prior_mean: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    prior_sd: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    demo_defaults: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
