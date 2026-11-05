"""Comandos do ImobScore, rodados com `python -m app.cli`."""

import csv
import json
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import numpy as np
import typer

from app.analysis.report import format_summary, read_pairs, write_report
from app.analysis.simulation import build_simulated_export
from app.config import get_settings
from app.db import SessionLocal
from app.engine import FEATURE_KEYS, MCMCConfig, ResultRow, evaluate_participant
from app.services.export_service import ExportError, write_export
from app.services.seed_service import (
    count_listings,
    count_sessions,
    load_personas,
    load_results,
    seed_database,
)

# No contêiner, a aplicação está em /app e os dados em /app/data; na máquina
# local, a aplicação está em backend/ e os dados em data/, na raiz do repositório.
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data" if (APP_DIR / "data").is_dir() else APP_DIR.parent / "data"
RESULTS_CSV = DATA_DIR / "results" / "results.csv"

app = typer.Typer(help="Comandos do ImobScore.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """Comandos do ImobScore."""


@app.command()
def seed(
    force: bool = typer.Option(
        False, "--force", help="Apaga tudo, mesmo com sessões já existentes."
    ),
    if_empty: bool = typer.Option(
        False, "--if-empty", help="Só semeia quando o catálogo está vazio."
    ),
    with_results: bool = typer.Option(
        False, "--with-results", help="Carrega também data/results/results.csv."
    ),
) -> None:
    """Recria catálogo, personas e estatísticas de padronização."""
    settings = get_settings()
    with SessionLocal() as session:
        if if_empty and count_listings(session) > 0:
            typer.echo("O catálogo já tem imóveis; nada foi recriado.")
        else:
            if not force and count_sessions(session) > 0:
                typer.echo("Existem sessões; use --force para apagar tudo", err=True)
                raise typer.Exit(code=1)

            stats = seed_database(session, settings)
            session.commit()
            typer.echo(
                f"Catálogo pronto: {stats.listings} imóveis, "
                f"{stats.personas} personas e {stats.feature_stats} linhas de feature_stats."
            )

        if with_results and RESULTS_CSV.exists():
            inserted = load_results(session, RESULTS_CSV)
            session.commit()
            typer.echo(f"Resultados: {inserted} linhas de {RESULTS_CSV.name}.")


@app.command()
def export(
    out: Annotated[
        Path,
        typer.Option("--out", help="Arquivo JSON onde os pares são gravados."),
    ],
) -> None:
    """Grava os pares respondidos da coleta em JSON."""
    with SessionLocal() as session:
        try:
            total = write_export(session, out)
        except ExportError as error:
            typer.echo(str(error), err=True)
            raise typer.Exit(code=1) from error

    if total == 0:
        typer.echo("Nenhuma sessão da coleta com pelo menos 20 pares respondidos.")
    typer.echo(f"Exportados {total} participantes para {out}.")


@app.command("load-results")
def load_results_command(
    csv_path: Annotated[Path, typer.Argument(help="Arquivo CSV de resultados.")],
) -> None:
    """Carrega as linhas de resultados do experimento em `experiment_results`.

    Se a rodada do arquivo já estiver no banco, nada é inserido e o comando avisa.
    """
    if not csv_path.exists():
        typer.echo(f"Arquivo não encontrado: {csv_path}", err=True)
        raise typer.Exit(code=1)

    run_ids = _csv_run_ids(csv_path)
    with SessionLocal() as session:
        inserted = load_results(session, csv_path)
        session.commit()

    if inserted:
        typer.echo(f"Resultados: {inserted} linhas de {csv_path.name}.")
        return
    if not run_ids:
        typer.echo(f"O arquivo {csv_path.name} está vazio.")
        return
    typer.echo(f"A rodada {run_ids[0]} já está no banco; nada foi inserido.", err=True)


def _csv_run_ids(path: Path) -> list[str]:
    """As rodadas do CSV, para avisar quando a rodada já está no banco."""
    with path.open(newline="", encoding="utf-8") as handle:
        return [row["run_id"] for row in csv.DictReader(handle)]


@app.command()
def simulate(
    participants: Annotated[
        int, typer.Option("--participants", help="Quantos participantes.")
    ] = 10,
    out: Annotated[
        Path, typer.Option("--out", help="Arquivo JSON onde os pares são gravados.")
    ] = DATA_DIR / "collected" / "pairs_simulated.json",
) -> None:
    """Cria participantes sintéticos (S01, S02...), no formato do export."""
    with SessionLocal() as session:
        payload = build_simulated_export(session, participants)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Simulados {participants} participantes em {out}.")


@app.command()
def evaluate(
    from_json: Annotated[
        Path, typer.Option("--from-json", help="Arquivo JSON do export ou da simulação.")
    ],
    out: Annotated[
        Path, typer.Option("--out", help="Pasta dos resultados e das figuras.")
    ] = DATA_DIR / "results",
) -> None:
    """Avalia os métodos em pares nunca vistos e grava CSVs e figuras. Não usa o banco."""
    settings = get_settings()
    cfg = MCMCConfig(
        chains=settings.mcmc_chains,
        warmup=settings.mcmc_warmup,
        draws=settings.mcmc_draws,
        thin=settings.mcmc_thin,
    )
    personas = {persona.slug: persona for persona in load_personas()}
    participants = read_pairs(from_json)
    if not participants:
        typer.echo(f"Nenhum participante em {from_json}.", err=True)
        raise typer.Exit(code=1)

    rows: list[ResultRow] = []
    for participant in participants:
        typer.echo(f"Avaliando {participant.participant_code}...")
        persona = personas[participant.persona_slug]
        rows += evaluate_participant(
            participant.participant_code,
            participant.D,
            np.array([persona.prior_mean[key] for key in FEATURE_KEYS]),
            np.array([persona.prior_sd[key] for key in FEATURE_KEYS]),
            cfg=cfg,
        )

    run_id = uuid4()
    summary = write_report(rows, run_id, out)
    typer.echo(format_summary(summary))
    typer.echo(f"Rodada {run_id}: resultados e figuras em {out}.")


if __name__ == "__main__":
    app()
