"""Serviço de posteriori: a linha de `posteriors` da sessão, ou o MCMC que a produz."""

from io import BytesIO

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.engine import (
    FEATURE_KEYS,
    FEATURES,
    MCMCConfig,
    MCMCResult,
    fit_posterior,
    is_ok,
    raw_matrix,
    seed_for,
    standardize,
)
from app.engine import Diagnostics as EngineDiagnostics
from app.errors import ApiError
from app.models import Comparison, FeatureStat, Listing, Persona, Posterior, SessionModel
from app.schemas.pair import Diagnostics
from app.schemas.posterior import PosteriorOut, TraceOut, WeightOut

N_FEATURES = len(FEATURE_KEYS)
TRACE_CHAINS = 4
# A semente do motor tem 64 bits sem sinal; a coluna `posteriors.seed` é um
# bigint com sinal. A conversão é uma bijeção, então a semente volta igual.
SEED_MODULO = 1 << 64
SIGNED_LIMIT = 1 << 63


def segment_center_scale(db: Session, session: SessionModel) -> tuple[np.ndarray, np.ndarray]:
    """O centro e a escala do segmento da sessão, na ordem de `FEATURE_KEYS`."""
    rows = db.execute(
        select(FeatureStat.feature_key, FeatureStat.center, FeatureStat.scale).where(
            FeatureStat.city == session.city,
            FeatureStat.purpose == session.purpose,
        )
    ).all()
    values = {key: (center, scale) for key, center, scale in rows}
    missing = [key for key in FEATURE_KEYS if key not in values]
    if missing:
        raise ValueError(f"O segmento da sessão não tem as estatísticas: {', '.join(missing)}.")
    center = np.array([values[key][0] for key in FEATURE_KEYS], dtype=np.float64)
    scale = np.array([values[key][1] for key in FEATURE_KEYS], dtype=np.float64)
    return center, scale


def standardized(db: Session, session: SessionModel, listings: list[Listing]) -> np.ndarray:
    """Z (n, 12) dos imóveis, padronizado pelo segmento da sessão."""
    center, scale = segment_center_scale(db, session)
    return standardize(raw_matrix(listings), center, scale)


def prior(db: Session, session: SessionModel) -> tuple[np.ndarray, np.ndarray]:
    """A média e o desvio da priori da persona, na ordem de `FEATURE_KEYS`."""
    persona = db.get(Persona, session.persona_slug)
    if persona is None:
        raise ValueError(f"A persona {session.persona_slug} não está no banco.")
    mu = np.array([float(persona.prior_mean[key]) for key in FEATURE_KEYS], dtype=np.float64)
    sd = np.array([float(persona.prior_sd[key]) for key in FEATURE_KEYS], dtype=np.float64)
    return mu, sd


def differences(db: Session, session: SessionModel, n: int) -> np.ndarray:
    """D (m, 12): z(vencedor) - z(perdedor) dos n primeiros pares respondidos."""
    comparisons = db.scalars(
        select(Comparison)
        .where(Comparison.session_id == session.id, Comparison.chosen.is_not(None))
        .order_by(Comparison.position)
        .limit(n)
    ).all()
    if not comparisons:
        return np.zeros((0, N_FEATURES), dtype=np.float64)

    winners: list[Listing] = []
    losers: list[Listing] = []
    for comparison in comparisons:
        left_won = comparison.chosen == "A"
        winner = db.get(Listing, comparison.listing_a_id if left_won else comparison.listing_b_id)
        loser = db.get(Listing, comparison.listing_b_id if left_won else comparison.listing_a_id)
        if winner is None or loser is None:  # pragma: no cover - o banco não deixa isso
            raise ApiError(404, "listing_not_found", "Imóvel do par não encontrado.")
        winners.append(winner)
        losers.append(loser)

    center, scale = segment_center_scale(db, session)
    winner_z = standardize(raw_matrix(winners), center, scale)
    loser_z = standardize(raw_matrix(losers), center, scale)
    return winner_z - loser_z


def get_or_fit(db: Session, session: SessionModel, n: int) -> MCMCResult:
    """A posteriori da sessão com n pares: a linha gravada, ou o MCMC que a produz.

    A linha é procurada de novo depois de travar a sessão, para que dois pedidos
    ao mesmo tempo não gravem duas linhas com o mesmo `(session_id, n_comparisons)`.
    """
    row = _find(db, session, n)
    if row is not None:
        return _from_row(row)

    db.refresh(session, with_for_update=True)
    row = _find(db, session, n)
    if row is not None:
        return _from_row(row)

    mu, sd = prior(db, session)
    result = fit_posterior(differences(db, session, n), mu, sd, seed_for(session.id, n), _config())
    _store(db, session, n, result)
    return result


def diagnostics_out(diagnostics: EngineDiagnostics) -> Diagnostics:
    """O diagnóstico do motor no schema da API."""
    return Diagnostics(
        accept_rate=diagnostics.accept_rate,
        rhat_max=diagnostics.rhat_max,
        ess_min=diagnostics.ess_min,
        step_size=diagnostics.step_size,
        elapsed_ms=diagnostics.elapsed_ms,
        ok=diagnostics.ok,
    )


def posterior_out(db: Session, session: SessionModel, n: int) -> PosteriorOut:
    """Os doze pesos da posteriori, com a priori da persona e os diagnósticos."""
    result = get_or_fit(db, session, n)
    mu, sd = prior(db, session)
    samples = result.samples
    mean = samples.mean(axis=0)
    deviation = samples.std(axis=0, ddof=1)
    ci_low, ci_high = np.percentile(samples, [5, 95], axis=0)

    weights = [
        WeightOut(
            feature_key=key,
            label=feature.label,
            prior_mean=float(mu[index]),
            prior_sd=float(sd[index]),
            post_mean=float(mean[index]),
            post_sd=float(deviation[index]),
            ci_low=float(ci_low[index]),
            ci_high=float(ci_high[index]),
        )
        for index, (key, feature) in enumerate(zip(FEATURE_KEYS, FEATURES, strict=True))
    ]
    return PosteriorOut(
        n_comparisons=n,
        weights=weights,
        diagnostics=diagnostics_out(result.diagnostics),
    )


def trace_out(db: Session, session: SessionModel, feature: str, n: int) -> TraceOut:
    """O traço das quatro primeiras cadeias de um peso."""
    if feature not in FEATURE_KEYS:
        raise ApiError(422, "validation_error", "Característica desconhecida.")

    result = get_or_fit(db, session, n)
    n_chains = get_settings().mcmc_chains
    index = FEATURE_KEYS.index(feature)
    chains = result.samples.reshape(n_chains, -1, N_FEATURES)[:TRACE_CHAINS, :, index]
    return TraceOut(
        feature_key=feature,
        chains=[[float(value) for value in chain] for chain in chains],
    )


def _config() -> MCMCConfig:
    """A configuração do MCMC das variáveis de ambiente."""
    settings = get_settings()
    return MCMCConfig(
        chains=settings.mcmc_chains,
        warmup=settings.mcmc_warmup,
        draws=settings.mcmc_draws,
        thin=settings.mcmc_thin,
    )


def _find(db: Session, session: SessionModel, n: int) -> Posterior | None:
    """A linha da posteriori com n pares, se existir."""
    return db.scalar(
        select(Posterior).where(
            Posterior.session_id == session.id,
            Posterior.n_comparisons == n,
        )
    )


def _from_row(row: Posterior) -> MCMCResult:
    """Monta o resultado do motor a partir da linha gravada."""
    samples = np.load(BytesIO(row.samples)).astype(np.float64)
    return MCMCResult(
        samples=samples,
        n_chains=get_settings().mcmc_chains,
        seed=_seed_unsigned(row.seed),
        diagnostics=EngineDiagnostics(
            accept_rate=row.accept_rate,
            rhat_max=row.rhat_max,
            ess_min=row.ess_min,
            step_size=row.step_size,
            elapsed_ms=row.elapsed_ms,
            # Sem pares, a linha guarda a amostragem da priori, com aceitação 1,0,
            # que o critério do motor recusa; a interface 5.10 diz que aí o `ok` é
            # verdadeiro.
            ok=row.n_comparisons == 0 or is_ok(row.accept_rate, row.rhat_max, row.ess_min),
        ),
    )


def _seed_signed(seed: int) -> int:
    """A semente de 64 bits sem sinal, no bigint com sinal do banco."""
    return seed - SEED_MODULO if seed >= SIGNED_LIMIT else seed


def _seed_unsigned(seed: int) -> int:
    """A semente do bigint com sinal, nos 64 bits sem sinal do motor."""
    return seed + SEED_MODULO if seed < 0 else seed


def _store(db: Session, session: SessionModel, n: int, result: MCMCResult) -> None:
    """Grava a linha da posteriori, com as amostras em `float32`."""
    samples = result.samples.astype(np.float32)
    buffer = BytesIO()
    np.save(buffer, samples)

    mean = result.samples.mean(axis=0)
    deviation = result.samples.std(axis=0, ddof=1)
    ci_low, ci_high = np.percentile(result.samples, [5, 95], axis=0)

    db.add(
        Posterior(
            session_id=session.id,
            n_comparisons=n,
            seed=_seed_signed(result.seed),
            samples=buffer.getvalue(),
            mean={key: float(mean[index]) for index, key in enumerate(FEATURE_KEYS)},
            sd={key: float(deviation[index]) for index, key in enumerate(FEATURE_KEYS)},
            ci_low={key: float(ci_low[index]) for index, key in enumerate(FEATURE_KEYS)},
            ci_high={key: float(ci_high[index]) for index, key in enumerate(FEATURE_KEYS)},
            accept_rate=result.diagnostics.accept_rate,
            rhat_max=result.diagnostics.rhat_max,
            ess_min=result.diagnostics.ess_min,
            step_size=result.diagnostics.step_size,
            elapsed_ms=result.diagnostics.elapsed_ms,
        )
    )
    db.flush()
