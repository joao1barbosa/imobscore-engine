"""Rotas da versão 1 da API."""

from fastapi import APIRouter

from app.api.v1 import experiment, feed, health, meta, posterior, sessions

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(meta.router, tags=["meta"])
router.include_router(sessions.router, tags=["sessions"])
router.include_router(feed.router, tags=["feed"])
router.include_router(posterior.router, tags=["posterior"])
router.include_router(experiment.router, tags=["experiment"])
