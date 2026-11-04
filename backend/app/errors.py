"""Erros da API no formato único do projeto: `{"detail": {"code", "message"}}`."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Erro com código e mensagem em português do Brasil."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def api_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Converte um `ApiError` no formato único da API."""
    if not isinstance(exc, ApiError):
        raise exc
    return JSONResponse(
        status_code=exc.status,
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Converte o `RequestValidationError` do FastAPI no formato único da API."""
    if not isinstance(exc, RequestValidationError):
        raise exc
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "validation_error",
                "message": "Dados inválidos na requisição.",
            }
        },
    )
