"""Schema do par mostrado e da resposta da pessoa."""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.listing import ListingCard


class Diagnostics(BaseModel):
    """Diagnóstico do MCMC (seção 5.4)."""

    accept_rate: float
    rhat_max: float
    ess_min: float
    step_size: float
    elapsed_ms: int
    ok: bool


class PairOut(BaseModel):
    """O par mostrado, com a posição e o total de pares da sessão."""

    position: int
    total: int
    listing_a: ListingCard
    listing_b: ListingCard


class AnswerIn(BaseModel):
    """A escolha da pessoa e quanto tempo ela levou."""

    chosen: Literal["A", "B"]
    response_ms: int = Field(ge=0, le=600_000)


class AnswerOut(BaseModel):
    """O estado da coleta depois da resposta.

    Na coleta, `diagnostics` é sempre `None`: o MCMC não roda entre os pares.
    """

    answered: int
    total: int
    done: bool
    diagnostics: Diagnostics | None = None
