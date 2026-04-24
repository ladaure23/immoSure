from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"champ": e["loc"][-1], "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "Données invalides", "erreurs": errors})


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Erreur non gérée sur {method} {path}", method=request.method, path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})
