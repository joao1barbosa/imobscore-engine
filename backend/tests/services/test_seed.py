"""Testes do seed: catálogo, personas, estatísticas e reprodutibilidade."""

from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from typer.testing import CliRunner

from app.cli import app
from app.config import get_settings
from app.models import ExperimentResult, FeatureStat, Listing, Persona, SessionModel
from app.services.seed_service import load_results, seed_database


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Engine do banco de teste."""
    settings = get_settings()
    test_engine: Engine = create_engine(settings.test_database_url, pool_pre_ping=True)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Sessão no banco de teste."""
    maker = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with maker() as test_session:
        yield test_session


@pytest.fixture
def cli(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    """Runner do Typer com o comando `seed` apontado para o banco de teste."""
    maker = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr("app.cli.SessionLocal", maker)
    return CliRunner()


def count(session: Session, model: type[Any]) -> int:
    """Quantas linhas a tabela tem."""
    return int(session.scalar(select(func.count()).select_from(model)) or 0)


def listings_snapshot(session: Session) -> list[tuple[str, Decimal]]:
    """Códigos e preços dos imóveis, em ordem."""
    rows = session.execute(select(Listing.code, Listing.price_brl).order_by(Listing.code)).all()
    return [(row[0], row[1]) for row in rows]


def test_seed_cria_catalogo_personas_e_estatisticas(session: Session) -> None:
    stats = seed_database(session, get_settings())
    session.commit()

    assert stats.listings == 300
    assert stats.personas == 3
    assert stats.feature_stats == 12
    assert count(session, Listing) == 300
    assert count(session, Persona) == 3
    assert count(session, FeatureStat) == 12


def test_seed_cobre_as_doze_caracteristicas(session: Session) -> None:
    seed_database(session, get_settings())
    session.commit()

    keys = session.scalars(select(FeatureStat.feature_key)).all()

    assert len(keys) == 12
    assert len(set(keys)) == 12
    scales = session.scalars(select(FeatureStat.scale)).all()
    assert all(scale > 0 for scale in scales)


def test_seed_rodado_duas_vezes_gera_os_mesmos_codigos_e_precos(session: Session) -> None:
    settings = get_settings()

    seed_database(session, settings)
    session.commit()
    first = listings_snapshot(session)

    seed_database(session, settings)
    session.commit()
    second = listings_snapshot(session)

    assert len(first) == 300
    assert first == second


def test_seed_preserva_o_codigo_e_o_preco_de_cada_imovel(session: Session) -> None:
    settings = get_settings()

    seed_database(session, settings)
    session.commit()
    before = dict(listings_snapshot(session))

    seed_database(session, settings)
    session.commit()
    after = dict(listings_snapshot(session))

    assert before == after
    assert all(price > 0 for price in after.values())


def test_seed_recusa_apagar_quando_ha_sessoes(cli: CliRunner, session: Session) -> None:
    seed_database(session, get_settings())
    session.add(
        SessionModel(
            mode="demo",
            city="Goiânia",
            purpose="sale",
            price_min=Decimal("100000.00"),
            price_max=Decimal("500000.00"),
            persona_slug="familia",
            target_pairs=3,
        )
    )
    session.commit()

    result = cli.invoke(app, ["seed"])

    assert result.exit_code == 1
    assert "Existem sessões; use --force para apagar tudo" in result.output


def test_seed_com_force_apaga_as_sessoes(cli: CliRunner, session: Session) -> None:
    seed_database(session, get_settings())
    session.add(
        SessionModel(
            mode="demo",
            city="Goiânia",
            purpose="sale",
            price_min=Decimal("100000.00"),
            price_max=Decimal("500000.00"),
            persona_slug="familia",
            target_pairs=3,
        )
    )
    session.commit()

    result = cli.invoke(app, ["seed", "--force"])

    assert result.exit_code == 0
    assert count(session, Listing) == 300
    assert count(session, Persona) == 3
    assert count(session, FeatureStat) == 12


def test_seed_com_if_empty_nao_recria_o_catalogo(cli: CliRunner, session: Session) -> None:
    seed_database(session, get_settings())
    session.commit()
    before = listings_snapshot(session)

    result = cli.invoke(app, ["seed", "--if-empty"])

    assert result.exit_code == 0
    assert listings_snapshot(session) == before


def test_seed_com_if_empty_ignora_sessoes_existentes(cli: CliRunner, session: Session) -> None:
    seed_database(session, get_settings())
    session.commit()
    session.add(
        SessionModel(
            mode="collection",
            city="Goiânia",
            purpose="sale",
            price_min=Decimal("100000.00"),
            price_max=Decimal("500000.00"),
            persona_slug="familia",
            target_pairs=25,
            participant_code="P01",
            consent_at=datetime.now(UTC),
        )
    )
    session.commit()
    before = listings_snapshot(session)

    result = cli.invoke(app, ["seed", "--if-empty"])

    assert result.exit_code == 0
    assert "O catálogo já tem imóveis; nada foi recriado." in result.output
    assert listings_snapshot(session) == before
    assert count(session, SessionModel) == 1


def test_load_results_carrega_o_csv_e_ignora_o_run_id_repetido(
    session: Session, tmp_path: Path
) -> None:
    csv_path = tmp_path / "results.csv"
    csv_path.write_text(
        "run_id,participant_code,method,n_train,split_seed,n_test,accuracy,log_loss\n"
        "11111111-1111-1111-1111-111111111111,S01,equal,5,7,10,0.5,0.69\n"
        "11111111-1111-1111-1111-111111111111,S01,bayes,5,7,10,0.7,0.61\n",
        encoding="utf-8",
    )

    inserted = load_results(session, csv_path)
    session.commit()

    assert inserted == 2
    assert count(session, ExperimentResult) == 2
    assert load_results(session, csv_path) == 0
