import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.proprietaire import ProprietaireCreate, ProprietaireUpdate, ProprietaireRead
from app.modules.proprietaires import service

router = APIRouter(prefix="/api/proprietaires", tags=["proprietaires"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[ProprietaireRead])
async def list_proprietaires(db: AsyncSession = Depends(get_db)):
    return await service.list_proprietaires(db)


@router.post("", response_model=ProprietaireRead, status_code=201)
async def create_proprietaire(payload: ProprietaireCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_proprietaire(payload, db)


@router.get("/{proprietaire_id}", response_model=ProprietaireRead)
async def get_proprietaire(proprietaire_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_proprietaire(proprietaire_id, db)


@router.put("/{proprietaire_id}", response_model=ProprietaireRead)
async def update_proprietaire(proprietaire_id: uuid.UUID, payload: ProprietaireUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_proprietaire(proprietaire_id, payload, db)
