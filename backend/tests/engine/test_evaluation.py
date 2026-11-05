"""Testes do protocolo de avaliação, da simulação e do relatório (seção 5.9)."""

import csv
import json
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest

from app.analysis.report import read_pairs, summarize, write_report
from app.engine import FEATURE_KEYS, MCMCConfig, ResultRow, evaluate_participant, simulate_choices
from app.engine.evaluation import _score
from app.engine.model import sigmoid

N = len(FEATURE_KEYS)
FAST = MCMCConfig(chains=4, warmup=100, draws=200, thin=4)


def oriented_pairs(w: np.ndarray, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    d = rng.standard_normal((n, N))
    wins = rng.random(n) < sigmoid(d @ w)
    return np.where(wins[:, None], d, -d)


def test_score_conta_meio_acerto_em_p_igual_a_meio() -> None:
    accuracy, _ = _score(np.array([0.9, 0.5, 0.2, 0.6]))

    assert accuracy == pytest.approx((1 + 0.5 + 0 + 1) / 4)


def test_score_limita_a_probabilidade_na_perda() -> None:
    _, log_loss = _score(np.array([0.0]))

    assert log_loss == pytest.approx(-np.log(1e-6))


def test_uma_linha_por_participante_metodo_treino_e_split() -> None:
    w = np.ones(N)
    D = oriented_pairs(w, 25, seed=1)

    rows = evaluate_participant("P01", D, w, np.ones(N), n_splits=2, cfg=FAST)

    assert len(rows) == 4 * 2 * 3
    assert {row.method for row in rows} == {"equal", "persona", "mle", "bayes"}
    assert {row.n_train for row in rows} == {3, 5, 10}
    assert {row.split_seed for row in rows} == {0, 1}
    assert all(row.n_test == 10 and 0.0 <= row.accuracy <= 1.0 for row in rows)


def test_vinte_pares_bastam_e_dezenove_nao() -> None:
    w = np.ones(N)

    rows = evaluate_participant(
        "P01", oriented_pairs(w, 20, seed=3), w, np.ones(N), n_splits=1, cfg=FAST
    )

    assert {row.n_train for row in rows} == {3, 5, 10}
    with pytest.raises(ValueError, match="são precisos 20"):
        evaluate_participant(
            "P02", oriented_pairs(w, 19, seed=4), w, np.ones(N), n_splits=1, cfg=FAST
        )


def test_metodos_sem_treino_nao_mudam_com_o_numero_de_pares() -> None:
    w = np.ones(N)
    D = oriented_pairs(w, 25, seed=2)

    rows = evaluate_participant("P01", D, w, np.ones(N), n_splits=1, cfg=FAST)

    for method in ("equal", "persona"):
        assert len({row.accuracy for row in rows if row.method == method}) == 1


def test_a_avaliacao_e_reproduzivel() -> None:
    w = np.ones(N)
    D = oriented_pairs(w, 25, seed=3)

    first = evaluate_participant("P01", D, w, np.ones(N), n_splits=2, cfg=FAST)
    second = evaluate_participant("P01", D, w, np.ones(N), n_splits=2, cfg=FAST)

    assert first == second


def test_treino_e_teste_nao_se_misturam(monkeypatch: pytest.MonkeyPatch) -> None:
    w = np.ones(N)
    D = oriented_pairs(w, 25, seed=4)
    seen_train: list[np.ndarray] = []
    seen_test: list[np.ndarray] = []

    from app.engine import evaluation

    real_fit = evaluation.fit_mle
    real_predict = evaluation.predict_proba

    def spy_fit(D_train: np.ndarray) -> np.ndarray:
        seen_train.append(D_train)
        return real_fit(D_train)

    def spy_predict(method: str, D_test: np.ndarray, **kwargs: object) -> np.ndarray:
        seen_test.append(D_test)
        return real_predict(method, D_test, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(evaluation, "fit_mle", spy_fit)
    monkeypatch.setattr(evaluation, "predict_proba", spy_predict)

    evaluate_participant("P01", D, w, np.ones(N), n_splits=1, n_train_list=(15,), cfg=FAST)

    train = {row.tobytes() for row in seen_train[0]}
    test = {row.tobytes() for row in seen_test[0]}
    assert len(train) == 15
    assert len(test) == 10
    assert not train & test


def test_participante_com_poucos_pares_avisa() -> None:
    with pytest.raises(ValueError, match="P01"):
        evaluate_participant("P01", np.zeros((19, N)), np.ones(N), np.ones(N), cfg=FAST)


def test_simulate_choices_segue_a_probabilidade_do_modelo() -> None:
    d = np.zeros((20_000, N))
    d[:, 0] = 1.0
    w = np.zeros(N)
    w[0] = float(np.log(3.0))  # P(A) = 0,75

    chosen = simulate_choices(d, w, np.random.default_rng(5))

    assert set(chosen) == {"A", "B"}
    assert np.mean(chosen == "A") == pytest.approx(0.75, abs=0.02)


def write_pairs_file(path: Path, chosen: str = "A") -> None:
    t_left = [1.0] * N
    t_right = [0.0] * N
    path.write_text(
        json.dumps(
            {
                "exported_at": "2026-11-08T12:05:00-03:00",
                "feature_keys": list(FEATURE_KEYS),
                "participants": [
                    {
                        "participant_code": "P01",
                        "session_id": None,
                        "persona_slug": "familia",
                        "city": "Goiânia",
                        "purpose": "sale",
                        "center": [0.0] * N,
                        "scale": [2.0] * N,
                        "pairs": [
                            {
                                "position": 1,
                                "left_code": "A",
                                "right_code": "B",
                                "t_left": t_left,
                                "t_right": t_right,
                                "chosen": chosen,
                                "response_ms": 100,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(("chosen", "sign"), [("A", 1.0), ("B", -1.0)])
def test_read_pairs_orienta_do_vencedor_para_o_perdedor(
    tmp_path: Path, chosen: str, sign: float
) -> None:
    path = tmp_path / "pairs.json"
    write_pairs_file(path, chosen)

    participant = read_pairs(path)[0]

    assert participant.participant_code == "P01"
    assert participant.D == pytest.approx(sign * 0.5 * np.ones((1, N)))


def test_read_pairs_recusa_outras_caracteristicas(tmp_path: Path) -> None:
    path = tmp_path / "pairs.json"
    write_pairs_file(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["feature_keys"] = ["outra"]
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="características"):
        read_pairs(path)


def test_summarize_faz_media_e_desvio_por_metodo_e_treino() -> None:
    rows = [
        ResultRow("P01", "bayes", 5, 0, 10, 0.6, 0.5),
        ResultRow("P01", "bayes", 5, 1, 10, 0.8, 0.7),
        ResultRow("P02", "bayes", 5, 0, 10, 0.7, 0.6),
        ResultRow("P01", "mle", 5, 0, 10, 0.5, 0.9),
    ]

    summary = {row.method: row for row in summarize(rows)}

    assert summary["bayes"].acc_mean == pytest.approx(0.7)
    assert summary["bayes"].acc_sd == pytest.approx(0.1)
    assert summary["bayes"].ll_mean == pytest.approx(0.6)
    assert summary["bayes"].n_participants == 2
    assert summary["mle"].n_participants == 1


def test_write_report_grava_os_arquivos_com_as_colunas_certas(tmp_path: Path) -> None:
    rows = [
        ResultRow("P01", method, n_train, 0, 10, 0.7, 0.5)
        for method in ("equal", "persona", "mle", "bayes")
        for n_train in (3, 5, 10, 15)
    ]
    run_id = uuid4()

    write_report(rows, run_id, tmp_path)

    with (tmp_path / "results.csv").open(encoding="utf-8") as file:
        results = list(csv.DictReader(file))
    with (tmp_path / "summary.csv").open(encoding="utf-8") as file:
        summary = list(csv.DictReader(file))
    assert len(results) == 16
    assert results[0]["run_id"] == str(run_id)
    assert list(results[0]) == [
        "run_id",
        "participant_code",
        "method",
        "n_train",
        "split_seed",
        "n_test",
        "accuracy",
        "log_loss",
    ]
    assert list(summary[0]) == [
        "method",
        "n_train",
        "acc_mean",
        "acc_sd",
        "ll_mean",
        "ll_sd",
        "n_participants",
    ]
    assert (tmp_path / "accuracy_vs_ntrain.png").stat().st_size > 0
    assert (tmp_path / "accuracy_by_participant.png").stat().st_size > 0
