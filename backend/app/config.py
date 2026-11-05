"""Configuração lida do ambiente (variáveis de ambiente e arquivo `.env`)."""

from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuração da seção 6 do plano, mais o banco de teste."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore"
    test_database_url: str = (
        "postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore_test"
    )
    mcmc_chains: int = 16
    mcmc_warmup: int = 1000
    mcmc_draws: int = 2000
    mcmc_thin: int = 8
    prior_sd: float = 1.0
    pairs_demo: int = 3
    pairs_product: int = 8
    pairs_collection: int = 20
    catalog_seed: int = 42
    log_level: str = "INFO"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: object) -> object:
        """Aceita `CORS_ORIGINS` como lista separada por vírgulas."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Devolve a configuração, lida uma única vez por processo."""
    return Settings()
