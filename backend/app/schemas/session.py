"""Schemas de sessão: o que o onboarding manda e o que a API devolve."""

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

Mode = Literal["product", "demo", "collection"]
PersonaSlug = Literal["familia", "investidor", "estudante"]
Purpose = Literal["sale", "rent"]
SessionStatus = Literal["comparing", "done"]


class SessionCreate(BaseModel):
    """O onboarding de uma sessão."""

    mode: Mode = "product"
    city: str
    purpose: Purpose
    price_min: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    price_max: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    persona_slug: PersonaSlug
    consent: bool = False

    @model_validator(mode="after")
    def check_onboarding(self) -> "SessionCreate":
        """Só Goiânia e compra, com a faixa de preço em ordem."""
        if self.city != "Goiânia":
            raise ValueError("Por enquanto, o ImobScore só funciona em Goiânia.")
        if self.purpose != "sale":
            raise ValueError("Por enquanto, o ImobScore só trabalha com imóveis à venda.")
        if self.price_min >= self.price_max:
            raise ValueError("O preço mínimo tem de ser menor que o preço máximo.")
        if self.mode == "collection" and not self.consent:
            raise ValueError("A coleta exige o consentimento.")
        return self


class SessionOut(BaseModel):
    """O estado da sessão e o progresso da coleta."""

    id: UUID
    mode: str
    city: str
    purpose: str
    price_min: Decimal
    price_max: Decimal
    persona_slug: str
    target_pairs: int
    answered: int
    status: SessionStatus
