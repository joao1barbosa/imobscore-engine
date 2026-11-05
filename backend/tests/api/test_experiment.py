"""Testes do experimento: o resumo vazio e o resumo de uma rodada."""

import statistics
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.seed_service import load_results, seed_database

RUN_ID = "11111111-1111-1111-1111-111111111111"
OTHER_RUN_ID = "22222222-2222-2222-2222-222222222222"
METHODS = ("bayes", "mle", "persona", "equal")

# A acurácia e a perda de cada participante, com dois métodos e duas divisões.
VALUES: dict[tuple[str, str], tuple[tuple[float, float], tuple[float, float]]] = {
    ("S01", "bayes"): ((0.70, 0.80), (0.40, 0.45)),
    ("S02", "bayes"): ((0.60, 0.70), (0.50, 0.55)),
    ("S01", "mle"): ((0.60, 0.70), (0.50, 0.55)),
    ("S02", "mle"): ((0.50, 0.60), (0.60, 0.65)),
    ("S01", "persona"): ((0.50, 0.60), (0.60, 0.65)),
    ("S02", "persona"): ((0.55, 0.65), (0.65, 0.70)),
    ("S01", "equal"): ((0.40, 0.50), (0.70, 0.75)),
    ("S02", "equal"): ((0.45, 0.55), (0.75, 0.80)),
}


@pytest.fixture
def seeded(db: Session) -> Session:
    """Semeia o catálogo de demonstração no banco do teste."""
    seed_database(db, get_settings())
    return db


def results_csv(path: Path, run_id: str, codes: tuple[str, ...]) -> Path:
    """Escreve um CSV de exemplo, com duas divisões por participante e método."""
    lines = ["run_id,participant_code,method,n_train,split_seed,n_test,accuracy,log_loss"]
    for code in codes:
        for method in METHODS:
            accuracies, log_losses = VALUES[(code, method)]
            for split, (accuracy, log_loss) in enumerate(
                zip(accuracies, log_losses, strict=True), start=1
            ):
                lines.append(f"{run_id},{code},{method},5,{split},10,{accuracy},{log_loss}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_resumo_vazio(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/v1/experiment/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] is None
    assert body["simulated"] is False
    assert body["participants"] == 0
    assert body["rows"] == []
    assert body["per_participant"] == []


def test_resumo_com_um_csv_de_exemplo(client: TestClient, seeded: Session, tmp_path: Path) -> None:
    path = results_csv(tmp_path / "results.csv", RUN_ID, ("S01", "S02"))
    assert load_results(seeded, path) == 16
    seeded.commit()

    response = client.get("/api/v1/experiment/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == RUN_ID
    assert body["simulated"] is True
    assert body["participants"] == 2
    assert len(body["rows"]) == 4

    by_method = {row["method"]: row for row in body["rows"]}
    bayes = by_method["bayes"]
    assert bayes["n_train"] == 5
    assert bayes["n_participants"] == 2
    assert bayes["acc_mean"] == pytest.approx(statistics.fmean([0.70, 0.80, 0.60, 0.70]))
    assert bayes["acc_sd"] == pytest.approx(statistics.stdev([0.70, 0.80, 0.60, 0.70]))
    assert bayes["ll_mean"] == pytest.approx(statistics.fmean([0.40, 0.45, 0.50, 0.55]))
    assert bayes["ll_sd"] == pytest.approx(statistics.stdev([0.40, 0.45, 0.50, 0.55]))

    assert len(body["per_participant"]) == 8
    codes = {row["participant_code"] for row in body["per_participant"]}
    assert codes == {"S01", "S02"}
    for row in body["per_participant"]:
        assert row["method"] in METHODS
    s01_bayes = next(
        row
        for row in body["per_participant"]
        if row["participant_code"] == "S01" and row["method"] == "bayes"
    )
    assert s01_bayes["acc_mean"] == pytest.approx(statistics.fmean([0.70, 0.80]))


def test_resumo_de_participantes_reais_nao_e_simulado(
    client: TestClient, seeded: Session, tmp_path: Path
) -> None:
    path = tmp_path / "results.csv"
    lines = ["run_id,participant_code,method,n_train,split_seed,n_test,accuracy,log_loss"]
    for method in METHODS:
        lines.append(f"{OTHER_RUN_ID},P01,{method},5,1,10,0.5,0.69")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert load_results(seeded, path) == 4
    seeded.commit()

    body = client.get("/api/v1/experiment/summary").json()

    assert body["run_id"] == OTHER_RUN_ID
    assert body["simulated"] is False
    assert body["participants"] == 1
    assert len(body["per_participant"]) == 4


def test_resumo_da_rodada_pedida(client: TestClient, seeded: Session, tmp_path: Path) -> None:
    first = results_csv(tmp_path / "first.csv", RUN_ID, ("S01",))
    second = results_csv(tmp_path / "second.csv", OTHER_RUN_ID, ("S02",))
    load_results(seeded, first)
    load_results(seeded, second)
    seeded.commit()

    body = client.get("/api/v1/experiment/summary", params={"run_id": RUN_ID}).json()

    assert body["run_id"] == RUN_ID
    assert body["participants"] == 1
    assert {row["participant_code"] for row in body["per_participant"]} == {"S01"}


def test_run_id_desconhecido_da_resumo_vazio(client: TestClient, seeded: Session) -> None:
    response = client.get(
        "/api/v1/experiment/summary",
        params={"run_id": "33333333-3333-3333-3333-333333333333"},
    )

    assert response.status_code == 200
    body: dict[str, Any] = response.json()
    assert body["rows"] == []
    assert body["per_participant"] == []
    assert body["participants"] == 0
