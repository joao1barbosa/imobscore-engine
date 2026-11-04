"""Tabela `posteriors`: amostras do MCMC e resumo, por sessão e por número de pares."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Integer,
    LargeBinary,
    SmallInteger,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Posterior(Base):
    __tablename__ = "posteriors"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    n_comparisons: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    samples: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    mean: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    sd: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    ci_low: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    ci_high: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    accept_rate: Mapped[float] = mapped_column(Float, nullable=False)
    rhat_max: Mapped[float] = mapped_column(Float, nullable=False)
    ess_min: Mapped[float] = mapped_column(Float, nullable=False)
    step_size: Mapped[float] = mapped_column(Float, nullable=False)
    elapsed_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (UniqueConstraint("session_id", "n_comparisons"),)
