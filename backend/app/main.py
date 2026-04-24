from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logger.remove()
logger.add(sys.stdout, level="DEBUG" if not settings.is_production else "INFO",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}")
logger.add("/var/log/immosure/app.log", rotation="50 MB", retention="30 days",
           level="INFO", compression="gz")


@app.get("/api/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
