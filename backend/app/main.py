from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from pathlib import Path
import sys

from app.config import settings
from app.database import engine, Base


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
# En dev : origins explicites ; en prod : domaine de l'app uniquement
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


@app.get("/api/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
