import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.proprietaire import ProprietaireCreate, ProprietaireUpdate, ProprietaireRead
from app.modules.proprietaires import service

router = APIRouter(prefix="/api/proprietaires", tags=["proprietaires"])


@router.get("", response_model=list[ProprietaireRead])
async def list_proprietaires(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.list_proprietaires(db, user)


@router.post("", response_model=ProprietaireRead, status_code=201)
async def create_proprietaire(payload: ProprietaireCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.create_proprietaire(payload, db, user)


@router.get("/{proprietaire_id}", response_model=ProprietaireRead)
async def get_proprietaire(proprietaire_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_proprietaire(proprietaire_id, db, user)


@router.put("/{proprietaire_id}", response_model=ProprietaireRead)
async def update_proprietaire(proprietaire_id: uuid.UUID, payload: ProprietaireUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.update_proprietaire(proprietaire_id, payload, db, user)
