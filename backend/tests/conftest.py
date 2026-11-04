"""Fixtures dos testes: banco de teste e cliente HTTP."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.deps import get_db
from app.main import app


@pytest.fixture
def db() -> Iterator[Session]:
    """Sessão numa transação que é revertida no fim de cada teste."""
    settings = get_settings()
    engine: Engine = create_engine(settings.test_database_url, pool_pre_ping=True)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    connection = engine.connect()
    transaction = connection.begin()
    session = testing_session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    """Cliente HTTP com `get_db` apontando para o banco de teste."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
