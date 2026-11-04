"""Comandos do ImobScore, rodados com `python -m app.cli`."""

from pathlib import Path

import typer

from app.config import get_settings
from app.db import SessionLocal
from app.services.seed_service import count_listings, count_sessions, load_results, seed_database

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_CSV = REPO_ROOT / "data" / "results" / "results.csv"

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


if __name__ == "__main__":
    app()
