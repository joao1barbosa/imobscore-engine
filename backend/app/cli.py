"""Comandos do ImobScore, rodados com `python -m app.cli`."""

from pathlib import Path
from typing import Annotated

import typer

from app.config import get_settings
from app.db import SessionLocal
from app.services.export_service import ExportError, write_export
from app.services.seed_service import count_listings, count_sessions, load_results, seed_database

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
        typer.echo("Nenhuma sessão da coleta com os 25 pares respondidos.")
    typer.echo(f"Exportados {total} participantes para {out}.")


if __name__ == "__main__":
    app()
