"""Testes do export: formato do JSON e regras dos participantes."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from typer.testing import CliRunner

from app.cli import app
from app.config import get_settings
from app.engine import FEATURE_KEYS, raw_matrix
from app.models import Comparison, FeatureStat, Listing, SessionModel
from app.services.export_service import build_export, write_export
from app.services.seed_service import seed_database


@pytest.fixture
def seeded(db: Session) -> Session:
    """Semeia o catálogo de demonstração no banco do teste."""
    seed_database(db, get_settings())
    return db


def add_collection(
    db: Session,
    *,
    answered: int = 25,
    pending: int = 0,
    code: str = "P01",
    mode: str = "collection",
) -> SessionModel:
    """Cria uma sessão com pares respondidos (e, se quiser, pendentes)."""
    collection = mode == "collection"
    session = SessionModel(
        mode=mode,
        city="Goiânia",
        purpose="sale",
        price_min=Decimal("300000.00"),
        price_max=Decimal("900000.00"),
        persona_slug="familia",
        target_pairs=25,
        participant_code=code if collection else None,
        consent_at=datetime.now(UTC) if collection else None,
    )
    db.add(session)
    db.flush()

    listings = list(
        db.scalars(select(Listing).order_by(Listing.code).limit(2 * (answered + pending))).all()
    )
    for index in range(answered + pending):
        left, right = listings[2 * index], listings[2 * index + 1]
        db.add(
            Comparison(
                session_id=session.id,
                position=index + 1,
                listing_a_id=left.id,
                listing_b_id=right.id,
                selection="random",
                chosen=("A" if index % 2 == 0 else "B") if index < answered else None,
                response_ms=1000 + index if index < answered else None,
            )
        )
    db.flush()
    return session


def test_export_traz_o_participante_com_os_vinte_e_cinco_pares(seeded: Session) -> None:
    session = add_collection(seeded)

    payload = build_export(seeded)

    assert payload["feature_keys"] == list(FEATURE_KEYS)
    assert len(payload["feature_keys"]) == 12
    assert payload["exported_at"].endswith("-03:00")

    assert len(payload["participants"]) == 1
    participant = payload["participants"][0]
    assert participant["participant_code"] == "P01"
    assert participant["session_id"] == str(session.id)
    assert participant["persona_slug"] == "familia"
    assert participant["city"] == "Goiânia"
    assert participant["purpose"] == "sale"
    assert len(participant["center"]) == 12
    assert len(participant["scale"]) == 12
    assert len(participant["pairs"]) == 25
    assert [pair["position"] for pair in participant["pairs"]] == list(range(1, 26))


def test_export_ignora_sessao_com_pares_de_menos(seeded: Session) -> None:
    add_collection(seeded, answered=24)

    payload = build_export(seeded)

    assert payload["participants"] == []


def test_export_ignora_sessao_que_nao_e_da_coleta(seeded: Session) -> None:
    add_collection(seeded, mode="demo")

    payload = build_export(seeded)

    assert payload["participants"] == []


def test_export_traz_so_os_pares_respondidos(seeded: Session) -> None:
    add_collection(seeded, answered=25, pending=3)

    payload = build_export(seeded)

    pairs = payload["participants"][0]["pairs"]
    assert len(pairs) == 25
    assert all(pair["chosen"] in ("A", "B") for pair in pairs)
    assert all(pair["response_ms"] is not None for pair in pairs)


def test_export_usa_o_centro_e_a_escala_do_segmento(seeded: Session) -> None:
    add_collection(seeded)
    rows = seeded.scalars(
        select(FeatureStat).where(
            FeatureStat.city == "Goiânia",
            FeatureStat.purpose == "sale",
        )
    ).all()
    stats = {row.feature_key: row for row in rows}

    participant = build_export(seeded)["participants"][0]

    assert participant["center"] == pytest.approx([stats[key].center for key in FEATURE_KEYS])
    assert participant["scale"] == pytest.approx([stats[key].scale for key in FEATURE_KEYS])
    assert all(scale > 0 for scale in participant["scale"])


def test_export_calcula_as_linhas_brutas_das_caracteristicas(seeded: Session) -> None:
    session = add_collection(seeded)

    participant = build_export(seeded)["participants"][0]
    pair = participant["pairs"][0]
    comparison = seeded.scalar(
        select(Comparison).where(
            Comparison.session_id == session.id,
            Comparison.position == pair["position"],
        )
    )
    assert comparison is not None
    left = seeded.get(Listing, comparison.listing_a_id)
    right = seeded.get(Listing, comparison.listing_b_id)
    assert left is not None and right is not None

    matrix = raw_matrix([left, right])
    assert pair["left_code"] == left.code
    assert pair["right_code"] == right.code
    assert pair["t_left"] == pytest.approx(list(matrix[0]))
    assert pair["t_right"] == pytest.approx(list(matrix[1]))


def test_export_da_cada_sessao_o_seu_codigo(seeded: Session) -> None:
    add_collection(seeded, code="P01")
    add_collection(seeded, code="P02")

    payload = build_export(seeded)

    codes = [participant["participant_code"] for participant in payload["participants"]]
    assert codes == ["P01", "P02"]


def test_write_export_grava_o_json_no_formato(seeded: Session, tmp_path: Path) -> None:
    add_collection(seeded)
    path = tmp_path / "collected" / "pairs.json"

    total = write_export(seeded, path)

    assert total == 1
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    assert list(payload) == ["exported_at", "feature_keys", "participants"]
    assert len(payload["participants"]) == 1
    assert len(payload["participants"][0]["pairs"]) == 25


def test_comando_export_grava_o_arquivo(
    seeded: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    add_collection(seeded)
    maker = sessionmaker(bind=seeded.get_bind(), autoflush=False, expire_on_commit=False)
    monkeypatch.setattr("app.cli.SessionLocal", maker)
    path = tmp_path / "pairs.json"

    result = CliRunner().invoke(app, ["export", "--out", str(path)])

    assert result.exit_code == 0
    assert "Exportados 1 participantes" in result.output
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["participants"][0]["participant_code"] == "P01"
