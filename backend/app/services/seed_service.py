"""Serviço de seed: popula catálogo, personas e estatísticas de padronização."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import Settings
from app.engine import FEATURE_KEYS, fit_stats, raw_matrix
from app.models import Base, ExperimentResult, FeatureStat, Listing, Persona, SessionModel
from app.seed import ListingRow, generate_catalog

PERSONAS_PATH = Path(__file__).resolve().parents[1] / "seed" / "personas.yaml"


@dataclass
class ListingFeatures:
    """Uma linha do catálogo com os tipos que o motor espera (`ListingLike`)."""

    price_brl: Decimal | float
    area_m2: Decimal | float
    bedrooms: int
    bathrooms: int
    parking: int
    dist_center_km: Decimal | float
    age_years: int
    kind: str
    leisure_count: int
    pet_friendly: bool
    doorman_24h: bool


@dataclass(frozen=True)
class PersonaSeed:
    """Uma persona do arquivo `personas.yaml`."""

    slug: str
    name: str
    description: str
    prior_mean: dict[str, float]
    prior_sd: dict[str, float]
    demo_defaults: dict[str, Any]


@dataclass(frozen=True)
class SeedStats:
    """Quantas linhas cada etapa do seed gravou."""

    listings: int
    personas: int
    feature_stats: int
    results: int


def load_personas(path: Path = PERSONAS_PATH) -> list[PersonaSeed]:
    """Lê as personas do YAML do arquiteto."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        PersonaSeed(
            slug=item["slug"],
            name=item["name"],
            description=item["description"],
            prior_mean={key: float(value) for key, value in item["prior_mean"].items()},
            prior_sd={key: float(value) for key, value in item["prior_sd"].items()},
            demo_defaults=dict(item["demo_defaults"]),
        )
        for item in raw
    ]


def truncate_all(session: Session) -> None:
    """Apaga todas as linhas de todas as tabelas, com `CASCADE`."""
    tables = ", ".join(sorted(Base.metadata.tables))
    session.execute(text(f"TRUNCATE TABLE {tables} CASCADE"))


def insert_listings(session: Session, rows: Sequence[ListingRow]) -> None:
    """Grava o catálogo simulado em `listings`."""
    session.add_all(
        Listing(
            code=row.code,
            city=row.city,
            purpose=row.purpose,
            kind=row.kind,
            title=row.title,
            neighborhood=row.neighborhood,
            price_brl=Decimal(str(row.price_brl)),
            area_m2=Decimal(str(row.area_m2)),
            bedrooms=row.bedrooms,
            bathrooms=row.bathrooms,
            parking=row.parking,
            dist_center_km=Decimal(str(row.dist_center_km)),
            age_years=row.age_years,
            leisure_count=row.leisure_count,
            pet_friendly=row.pet_friendly,
            doorman_24h=row.doorman_24h,
            illustration=row.illustration,
        )
        for row in rows
    )


def insert_personas(session: Session, personas: Sequence[PersonaSeed]) -> None:
    """Grava as personas em `personas`."""
    session.add_all(
        Persona(
            slug=persona.slug,
            name=persona.name,
            description=persona.description,
            prior_mean=dict(persona.prior_mean),
            prior_sd=dict(persona.prior_sd),
            demo_defaults=dict(persona.demo_defaults),
        )
        for persona in personas
    )


def insert_feature_stats(session: Session, rows: Sequence[ListingRow]) -> int:
    """Grava centro e escala de cada característica, por segmento (cidade, finalidade)."""
    segments: dict[tuple[str, str], list[ListingRow]] = {}
    for row in rows:
        segments.setdefault((row.city, row.purpose), []).append(row)

    stats: list[FeatureStat] = []
    for (city, purpose), segment in sorted(segments.items()):
        matrix = raw_matrix([_features(row) for row in segment])
        center, scale = fit_stats(matrix)
        for index, key in enumerate(FEATURE_KEYS):
            stats.append(
                FeatureStat(
                    city=city,
                    purpose=purpose,
                    feature_key=key,
                    center=float(center[index]),
                    scale=float(scale[index]),
                )
            )
    session.add_all(stats)
    return len(stats)


def seed_database(session: Session, settings: Settings) -> SeedStats:
    """Apaga tudo e popula catálogo, personas e estatísticas.

    A transação fica com quem chamou: o serviço só faz `flush`.
    """
    catalog = generate_catalog(settings.catalog_seed)
    personas = load_personas()
    truncate_all(session)
    insert_listings(session, catalog)
    insert_personas(session, personas)
    feature_stats = insert_feature_stats(session, catalog)
    session.flush()
    return SeedStats(
        listings=len(catalog),
        personas=len(personas),
        feature_stats=feature_stats,
        results=0,
    )


def load_results(session: Session, path: Path) -> int:
    """Insere as linhas de um CSV de resultados em `experiment_results`.

    O CSV tem as colunas `run_id, participant_code, method, n_train, split_seed,
    n_test, accuracy, log_loss`. Se o `run_id` já existir no banco, nada é
    inserido. Devolve quantas linhas foram inseridas.
    """
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return 0

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["run_id"], []).append(row)

    existing = {
        str(run_id) for run_id in session.scalars(select(ExperimentResult.run_id).distinct())
    }
    inserted = 0
    for run_id, group in grouped.items():
        if run_id in existing:
            continue
        session.add_all(
            ExperimentResult(
                run_id=UUID(run_id),
                participant_code=row["participant_code"],
                method=row["method"],
                n_train=int(row["n_train"]),
                split_seed=int(row["split_seed"]),
                n_test=int(row["n_test"]),
                accuracy=float(row["accuracy"]),
                log_loss=float(row["log_loss"]),
            )
            for row in group
        )
        inserted += len(group)
    return inserted


def count_listings(session: Session) -> int:
    """Quantos imóveis estão em `listings`."""
    return int(session.scalar(select(func.count()).select_from(Listing)) or 0)


def count_sessions(session: Session) -> int:
    """Quantas sessões estão em `sessions`."""
    return int(session.scalar(select(func.count()).select_from(SessionModel)) or 0)


def _features(row: ListingRow) -> ListingFeatures:
    """Converte uma linha do catálogo no formato que o motor espera."""
    return ListingFeatures(
        price_brl=row.price_brl,
        area_m2=row.area_m2,
        bedrooms=row.bedrooms,
        bathrooms=row.bathrooms,
        parking=row.parking,
        dist_center_km=row.dist_center_km,
        age_years=row.age_years,
        kind=row.kind,
        leisure_count=row.leisure_count,
        pet_friendly=row.pet_friendly,
        doorman_24h=row.doorman_24h,
    )
