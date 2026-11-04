"""Rotas da versão 1 da API."""

from fastapi import APIRouter

from app.api.v1 import health, meta, sessions

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(meta.router, tags=["meta"])
router.include_router(sessions.router, tags=["sessions"])
