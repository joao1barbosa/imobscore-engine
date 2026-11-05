"""Testes do comando `load-results`: o CSV entra no banco e a rodada repetida avisa."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, func, select, text
from sqlalchemy.orm import Session, sessionmaker
from typer.testing import CliRunner

from app.cli import app
from app.config import get_settings
from app.models import ExperimentResult

RUN_ID = "11111111-1111-1111-1111-111111111111"
CSV = (
    "run_id,participant_code,method,n_train,split_seed,n_test,accuracy,log_loss\n"
    f"{RUN_ID},S01,equal,5,1,10,0.5,0.69\n"
    f"{RUN_ID},S01,bayes,5,1,10,0.7,0.61\n"
)


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Engine do banco de teste."""
    settings = get_settings()
    test_engine: Engine = create_engine(settings.test_database_url, pool_pre_ping=True)
    yield test_engine
    test_engine.dispose()


@pytest.fixture(autouse=True)
def clean_results(engine: Engine) -> Iterator[None]:
    """Limpa a tabela de resultados antes e depois de cada teste."""
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE experiment_results CASCADE"))
    yield
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE experiment_results CASCADE"))


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Sessão no banco de teste."""
    maker = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with maker() as test_session:
        yield test_session


@pytest.fixture
def cli(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    """Runner do Typer com o comando `load-results` apontado para o banco de teste."""
    maker = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr("app.cli.SessionLocal", maker)
    return CliRunner()


def count(session: Session) -> int:
    """Quantas linhas a tabela de resultados tem."""
    return int(session.scalar(select(func.count()).select_from(ExperimentResult)) or 0)


def test_load_results_carrega_o_csv(cli: CliRunner, session: Session, tmp_path: Path) -> None:
    csv_path = tmp_path / "results.csv"
    csv_path.write_text(CSV, encoding="utf-8")

    result = cli.invoke(app, ["load-results", str(csv_path)])

    assert result.exit_code == 0
    assert "Resultados: 2 linhas" in result.output
    assert count(session) == 2
    run_ids = session.scalars(select(ExperimentResult.run_id).distinct()).all()
    assert [str(run_id) for run_id in run_ids] == [RUN_ID]


def test_load_results_com_a_rodada_repetida_avisa_e_nao_insere(
    cli: CliRunner, session: Session, tmp_path: Path
) -> None:
    csv_path = tmp_path / "results.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    assert cli.invoke(app, ["load-results", str(csv_path)]).exit_code == 0

    result = cli.invoke(app, ["load-results", str(csv_path)])

    assert result.exit_code == 0
    assert "já está no banco" in result.output
    assert count(session) == 2


def test_load_results_com_arquivo_que_nao_existe(cli: CliRunner, tmp_path: Path) -> None:
    result = cli.invoke(app, ["load-results", str(tmp_path / "ausente.csv")])

    assert result.exit_code == 1
    assert "Arquivo não encontrado" in result.output


def test_load_results_com_arquivo_vazio(cli: CliRunner, session: Session, tmp_path: Path) -> None:
    csv_path = tmp_path / "results.csv"
    csv_path.write_text(
        "run_id,participant_code,method,n_train,split_seed,n_test,accuracy,log_loss\n",
        encoding="utf-8",
    )

    result = cli.invoke(app, ["load-results", str(csv_path)])

    assert result.exit_code == 0
    assert "está vazio" in result.output
    assert count(session) == 0
