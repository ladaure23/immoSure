import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.agence import AgenceCreate, AgenceUpdate, AgenceRead
from app.modules.agences import service

router = APIRouter(prefix="/api/agences", tags=["agences"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[AgenceRead])
async def list_agences(db: AsyncSession = Depends(get_db)):
    return await service.list_agences(db)


@router.post("", response_model=AgenceRead, status_code=201)
async def create_agence(payload: AgenceCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_agence(payload, db)


@router.get("/{agence_id}", response_model=AgenceRead)
async def get_agence(agence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_agence(agence_id, db)


@router.put("/{agence_id}", response_model=AgenceRead)
async def update_agence(agence_id: uuid.UUID, payload: AgenceUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_agence(agence_id, payload, db)
