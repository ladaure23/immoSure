import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.bien import BienCreate, BienUpdate, BienRead
from app.modules.biens import service

router = APIRouter(prefix="/api/biens", tags=["biens"])


@router.get("", response_model=list[BienRead])
async def list_biens(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.list_biens(db, user)


@router.post("", response_model=BienRead, status_code=201)
async def create_bien(payload: BienCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.create_bien(payload, db, user)


@router.get("/{bien_id}", response_model=BienRead)
async def get_bien(bien_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_bien(bien_id, db, user)


@router.put("/{bien_id}", response_model=BienRead)
async def update_bien(bien_id: uuid.UUID, payload: BienUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.update_bien(bien_id, payload, db, user)
