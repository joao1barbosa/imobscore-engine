"""Rotas de metadados: os segmentos do catálogo e as personas."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Listing, Persona
from app.schemas.meta import DemoDefaults, MetaOptions, PersonaOut, SegmentOptions
from app.services.seed_service import load_personas

router = APIRouter()


@router.get("/meta/options", response_model=MetaOptions)
def meta_options(db: Annotated[Session, Depends(get_db)]) -> MetaOptions:
    """As faixas de preço de cada segmento do catálogo."""
    rows = db.execute(
        select(
            Listing.city,
            Listing.purpose,
            func.min(Listing.price_brl),
            func.max(Listing.price_brl),
        )
        .group_by(Listing.city, Listing.purpose)
        .order_by(Listing.city, Listing.purpose)
    ).all()

    return MetaOptions(
        segments=[
            SegmentOptions(
                city=city,
                purpose=purpose,
                price_floor=float(price_floor),
                price_ceiling=float(price_ceiling),
            )
            for city, purpose, price_floor, price_ceiling in rows
        ]
    )


@router.get("/meta/personas", response_model=list[PersonaOut])
def meta_personas(db: Annotated[Session, Depends(get_db)]) -> list[PersonaOut]:
    """As três personas, com a faixa de preço da demo.

    A ordem é a do arquivo `personas.yaml`, a mesma dos mockups aprovados.
    """
    personas = {persona.slug: persona for persona in db.scalars(select(Persona)).all()}
    order = [persona.slug for persona in load_personas()]
    ordered = [personas[slug] for slug in order if slug in personas]
    ordered += [persona for slug, persona in personas.items() if slug not in order]

    return [
        PersonaOut(
            slug=persona.slug,
            name=persona.name,
            description=persona.description,
            demo_defaults=DemoDefaults(
                city=str(persona.demo_defaults["city"]),
                purpose=str(persona.demo_defaults["purpose"]),
                price_min=float(persona.demo_defaults["price_min"]),
                price_max=float(persona.demo_defaults["price_max"]),
            ),
        )
        for persona in ordered
    ]
