import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.locataire import LocataireCreate, LocataireUpdate, LocataireRead, WalletInfo
from app.modules.locataires import service

router = APIRouter(prefix="/api/locataires", tags=["locataires"])


@router.get("", response_model=list[LocataireRead])
async def list_locataires(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.list_locataires(db, user)


@router.post("", response_model=LocataireRead, status_code=201)
async def create_locataire(payload: LocataireCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.create_locataire(payload, db, user)


@router.get("/{locataire_id}", response_model=LocataireRead)
async def get_locataire(locataire_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_locataire(locataire_id, db, user)


@router.put("/{locataire_id}", response_model=LocataireRead)
async def update_locataire(locataire_id: uuid.UUID, payload: LocataireUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.update_locataire(locataire_id, payload, db, user)


@router.get("/{locataire_id}/wallet", response_model=WalletInfo)
async def get_wallet(locataire_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_wallet(locataire_id, db, user)
