"""Teste da migração inicial: sobe, desce e sobe de novo no banco de teste."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.config import get_settings

BACKEND_DIR = Path(__file__).resolve().parents[1]

EXPECTED_TABLES = {
    "comparisons",
    "experiment_results",
    "feature_stats",
    "inspections",
    "listings",
    "personas",
    "posteriors",
    "sessions",
}


@pytest.fixture
def alembic_config() -> Config:
    """Configuração do Alembic apontada para o banco de teste."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    url = get_settings().test_database_url.replace("%", "%%")
    config.set_main_option("sqlalchemy.url", url)
    return config


def table_names(url: str) -> set[str]:
    """Lista as tabelas que existem no banco."""
    engine = create_engine(url)
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_migration_upgrade_downgrade(alembic_config: Config) -> None:
    url = get_settings().test_database_url

    command.upgrade(alembic_config, "head")
    assert table_names(url) == EXPECTED_TABLES | {"alembic_version"}

    command.downgrade(alembic_config, "base")
    assert table_names(url) == {"alembic_version"}

    command.upgrade(alembic_config, "head")
    assert table_names(url) == EXPECTED_TABLES | {"alembic_version"}
