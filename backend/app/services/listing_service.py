"""Serviço de imóveis: os candidatos de uma sessão e o cartão de cada um."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Listing, SessionModel
from app.schemas.listing import ListingCard

PRICE_FLOOR_FACTOR = Decimal("0.85")
PRICE_CEILING_FACTOR = Decimal("1.15")
MIN_CANDIDATES = 20


def candidate_listings(db: Session, session: SessionModel) -> list[Listing]:
    """Os imóveis candidatos da sessão, sempre ordenados por `code`.

    São os imóveis da cidade e da finalidade da sessão com preço entre
    0,85 × `price_min` e 1,15 × `price_max`. Se forem menos de 20, vale o
    segmento inteiro.
    """
    narrow = db.scalars(
        select(Listing)
        .where(
            Listing.city == session.city,
            Listing.purpose == session.purpose,
            Listing.price_brl >= session.price_min * PRICE_FLOOR_FACTOR,
            Listing.price_brl <= session.price_max * PRICE_CEILING_FACTOR,
        )
        .order_by(Listing.code)
    ).all()
    if len(narrow) >= MIN_CANDIDATES:
        return list(narrow)

    return list(
        db.scalars(
            select(Listing)
            .where(Listing.city == session.city, Listing.purpose == session.purpose)
            .order_by(Listing.code)
        ).all()
    )


def listing_card(listing: Listing) -> ListingCard:
    """Monta o cartão de um imóvel."""
    return ListingCard(
        id=listing.id,
        code=listing.code,
        title=listing.title,
        neighborhood=listing.neighborhood,
        city=listing.city,
        purpose=listing.purpose,
        kind=listing.kind,
        price_brl=listing.price_brl,
        area_m2=float(listing.area_m2),
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        parking=listing.parking,
        dist_center_km=float(listing.dist_center_km),
        age_years=listing.age_years,
        leisure_count=listing.leisure_count,
        pet_friendly=listing.pet_friendly,
        doorman_24h=listing.doorman_24h,
        illustration=listing.illustration,
    )
