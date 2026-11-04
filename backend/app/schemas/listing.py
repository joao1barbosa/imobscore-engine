"""Schema do cartão de imóvel."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ListingCard(BaseModel):
    """Um imóvel, como aparece no cartão da coleta."""

    id: UUID
    code: str
    title: str
    neighborhood: str
    city: str
    purpose: str
    kind: str
    price_brl: Decimal
    area_m2: float
    bedrooms: int
    bathrooms: int
    parking: int
    dist_center_km: float
    age_years: int
    leisure_count: int
    pet_friendly: bool
    doorman_24h: bool
    illustration: str
