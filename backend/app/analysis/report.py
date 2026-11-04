"""Lê os pares exportados e grava `results.csv`, `summary.csv` e as figuras (seção 5.9)."""

import csv
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from app.engine import FEATURE_KEYS, Method, ResultRow, standardize  # noqa: E402

# Os mesmos métodos, na mesma ordem e nas mesmas cores do painel do experimento (M7).
METHODS: tuple[Method, ...] = ("bayes", "mle", "persona", "equal")
METHOD_LABELS: dict[Method, str] = {
    "bayes": "Motor bayesiano",
    "mle": "Regressão logística",
    "persona": "Média da persona",
    "equal": "Pesos iguais",
}
METHOD_COLORS: dict[Method, str] = {
    "bayes": "#2a78d6",
    "mle": "#eb6834",
    "persona": "#1baf7a",
    "equal": "#eda100",
}
BY_PARTICIPANT_N_TRAIN = 5

RESULT_COLUMNS = (
    "run_id",
    "participant_code",
    "method",
    "n_train",
    "split_seed",
    "n_test",
    "accuracy",
    "log_loss",
)
SUMMARY_COLUMNS = ("method", "n_train", "acc_mean", "acc_sd", "ll_mean", "ll_sd", "n_participants")


@dataclass(frozen=True)
class SummaryRow:
    method: Method
    n_train: int
    acc_mean: float
    acc_sd: float
    ll_mean: float
    ll_sd: float
    n_participants: int


@dataclass(frozen=True)
class ParticipantPairs:
    participant_code: str
    persona_slug: str
    D: np.ndarray


def read_pairs(path: Path) -> list[ParticipantPairs]:
    """Lê o JSON do export e orienta cada par do vencedor para o perdedor."""
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if tuple(payload["feature_keys"]) != FEATURE_KEYS:
        raise ValueError("As características do arquivo não são as do motor.")

    participants = []
    for item in payload["participants"]:
        center = np.array(item["center"])
        scale = np.array(item["scale"])
        z_left = standardize(np.array([p["t_left"] for p in item["pairs"]]), center, scale)
        z_right = standardize(np.array([p["t_right"] for p in item["pairs"]]), center, scale)
        left_won = np.array([p["chosen"] == "A" for p in item["pairs"]])
        participants.append(
            ParticipantPairs(
                participant_code=item["participant_code"],
                persona_slug=item["persona_slug"],
                D=np.where(left_won[:, None], z_left - z_right, z_right - z_left),
            )
        )
    return participants


def summarize(rows: Sequence[ResultRow]) -> list[SummaryRow]:
    """Média e desvio padrão amostral sobre as linhas de cada método e n_train."""
    summary = []
    for n_train in sorted({row.n_train for row in rows}):
        for method in METHODS:
            selected = [row for row in rows if row.method == method and row.n_train == n_train]
            if not selected:
                continue
            accuracy = np.array([row.accuracy for row in selected])
            log_loss = np.array([row.log_loss for row in selected])
            summary.append(
                SummaryRow(
                    method=method,
                    n_train=n_train,
                    acc_mean=float(accuracy.mean()),
                    acc_sd=float(accuracy.std(ddof=1)) if accuracy.size > 1 else 0.0,
                    ll_mean=float(log_loss.mean()),
                    ll_sd=float(log_loss.std(ddof=1)) if log_loss.size > 1 else 0.0,
                    n_participants=len({row.participant_code for row in selected}),
                )
            )
    return summary


def write_results(rows: Sequence[ResultRow], run_id: UUID, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(RESULT_COLUMNS)
        for row in rows:
            writer.writerow(
                (
                    run_id,
                    row.participant_code,
                    row.method,
                    row.n_train,
                    row.split_seed,
                    row.n_test,
                    row.accuracy,
                    row.log_loss,
                )
            )


def write_summary(summary: Sequence[SummaryRow], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(SUMMARY_COLUMNS)
        for row in summary:
            writer.writerow(
                (
                    row.method,
                    row.n_train,
                    row.acc_mean,
                    row.acc_sd,
                    row.ll_mean,
                    row.ll_sd,
                    row.n_participants,
                )
            )


def format_summary(summary: Sequence[SummaryRow]) -> str:
    """A tabela resumo para o terminal."""
    lines = [f"{'método':<22}{'pares':>6}{'acurácia':>11}{'desvio':>9}{'perda':>9}{'pessoas':>9}"]
    for row in summary:
        lines.append(
            f"{METHOD_LABELS[row.method]:<22}{row.n_train:>6}{row.acc_mean:>11.3f}"
            f"{row.acc_sd:>9.3f}{row.ll_mean:>9.3f}{row.n_participants:>9}"
        )
    return "\n".join(lines)


def _style(axis: Any) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", color="#e2e6e8", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")


def plot_accuracy_vs_ntrain(summary: Sequence[SummaryRow], path: Path) -> None:
    """Uma linha por método, com faixa de ±1 desvio."""
    figure, axis = plt.subplots(figsize=(8, 5), layout="constrained")
    for method in METHODS:
        selected = [row for row in summary if row.method == method]
        if not selected:
            continue
        x = np.array([row.n_train for row in selected])
        mean = np.array([row.acc_mean for row in selected])
        sd = np.array([row.acc_sd for row in selected])
        color = METHOD_COLORS[method]
        axis.fill_between(x, mean - sd, mean + sd, color=color, alpha=0.10, linewidth=0)
        axis.plot(x, mean, color=color, linewidth=2, marker="o", label=METHOD_LABELS[method])

    axis.set_xticks(sorted({row.n_train for row in summary}))
    axis.set_ylim(0.2, 1.0)
    axis.set_xlabel("Pares usados no treino")
    axis.set_ylabel("Acurácia em pares nunca vistos")
    axis.set_title("Acurácia por número de pares de treino", loc="left")
    axis.legend(frameon=False)
    _style(axis)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def plot_accuracy_by_participant(rows: Sequence[ResultRow], path: Path) -> None:
    """Barras por participante e método, com n_train = 5."""
    selected = [row for row in rows if row.n_train == BY_PARTICIPANT_N_TRAIN]
    codes = sorted({row.participant_code for row in selected})
    figure, axis = plt.subplots(figsize=(max(8.0, 0.8 * len(codes)), 5), layout="constrained")

    width = 0.2
    for position, method in enumerate(METHODS):
        means = [
            np.mean(
                [
                    row.accuracy
                    for row in selected
                    if row.participant_code == code and row.method == method
                ]
            )
            for code in codes
        ]
        axis.bar(
            np.arange(len(codes)) + (position - 1.5) * width,
            means,
            width=width * 0.9,
            color=METHOD_COLORS[method],
            label=METHOD_LABELS[method],
        )

    axis.set_xticks(np.arange(len(codes)), codes)
    axis.set_ylim(0.0, 1.0)
    axis.set_xlabel("Participante")
    axis.set_ylabel("Acurácia em pares nunca vistos")
    axis.set_title(f"Acurácia por participante, com {BY_PARTICIPANT_N_TRAIN} pares", loc="left")
    figure.legend(frameon=False, ncols=len(METHODS), loc="outside lower center")
    _style(axis)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def write_report(rows: Sequence[ResultRow], run_id: UUID, out_dir: Path) -> list[SummaryRow]:
    """Grava os dois CSVs e as duas figuras em `out_dir`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows)
    write_results(rows, run_id, out_dir / "results.csv")
    write_summary(summary, out_dir / "summary.csv")
    plot_accuracy_vs_ntrain(summary, out_dir / "accuracy_vs_ntrain.png")
    plot_accuracy_by_participant(rows, out_dir / "accuracy_by_participant.png")
    return summary
