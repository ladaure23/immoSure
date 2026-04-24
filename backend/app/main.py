from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from pathlib import Path
import sys

from app.config import settings
from app.database import engine, Base
from app.middleware.logging import LoggingMiddleware
from app.middleware.errors import validation_exception_handler, global_exception_handler
from fastapi.exceptions import RequestValidationError

from app.modules.auth.router import router as auth_router
from app.modules.agences.router import router as agences_router
from app.modules.proprietaires.router import router as proprietaires_router
from app.modules.locataires.router import router as locataires_router
from app.modules.biens.router import router as biens_router
from app.modules.contrats.router import router as contrats_router
from app.modules.payments.router import router as payments_router
from app.modules.tickets.router import router as tickets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting ImmoSure [{settings.environment}]")
    yield
    await engine.dispose()
    logger.info("ImmoSure shutdown complete")


app = FastAPI(
    title="ImmoSure API",
    version="1.0.0",
    description="Plateforme de gestion locative automatisée — Bénin",
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS — allow_credentials=True est incompatible avec allow_origins=["*"]
_cors_origins = (
    ["http://localhost:3000", "http://127.0.0.1:3000"]
    if not settings.is_production
    else [settings.app_url]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# Logging setup — fichier log uniquement si le dossier existe (évite crash en dev)
logger.remove()
logger.add(
    sys.stdout,
    level="DEBUG" if not settings.is_production else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
)
_log_file = Path("/var/log/immosure/app.log")
if _log_file.parent.exists():
    logger.add(
        str(_log_file),
        rotation="50 MB",
        retention="30 days",
        level="INFO",
        compression="gz",
    )

# Error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(auth_router)
app.include_router(agences_router)
app.include_router(proprietaires_router)
app.include_router(locataires_router)
app.include_router(biens_router)
app.include_router(contrats_router)
app.include_router(payments_router)
app.include_router(tickets_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
