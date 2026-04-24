import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.bien import BienCreate, BienUpdate, BienRead
from app.modules.biens import service

router = APIRouter(prefix="/api/biens", tags=["biens"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[BienRead])
async def list_biens(db: AsyncSession = Depends(get_db)):
    return await service.list_biens(db)


@router.post("", response_model=BienRead, status_code=201)
async def create_bien(payload: BienCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_bien(payload, db)


@router.get("/{bien_id}", response_model=BienRead)
async def get_bien(bien_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_bien(bien_id, db)


@router.put("/{bien_id}", response_model=BienRead)
async def update_bien(bien_id: uuid.UUID, payload: BienUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_bien(bien_id, payload, db)
