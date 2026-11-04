"""Schemas de metadados: os segmentos do catálogo e as personas."""

from pydantic import BaseModel


class SegmentOptions(BaseModel):
    """Um segmento do catálogo, com a faixa de preço."""

    city: str
    purpose: str
    price_floor: float
    price_ceiling: float


class MetaOptions(BaseModel):
    """As opções de segmentação para o onboarding."""

    segments: list[SegmentOptions]


class DemoDefaults(BaseModel):
    """A faixa de preço que a demo de uma persona usa."""

    city: str
    purpose: str
    price_min: float
    price_max: float


class PersonaOut(BaseModel):
    """Uma persona, sem os pesos da priori."""

    slug: str
    name: str
    description: str
    demo_defaults: DemoDefaults
