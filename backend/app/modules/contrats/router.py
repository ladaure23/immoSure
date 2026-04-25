import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.contrat import ContratCreate, ContratUpdate, ContratRead, ContratRisque
from app.modules.contrats import service

router = APIRouter(prefix="/api/contrats", tags=["contrats"])


@router.get("", response_model=list[ContratRead])
async def list_contrats(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.list_contrats(db, user)


@router.post("", response_model=ContratRead, status_code=201)
async def create_contrat(payload: ContratCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.create_contrat(payload, db, user)


@router.get("/risques", response_model=list[ContratRisque])
async def get_contrats_a_risque(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_contrats_a_risque(db, user)


@router.get("/{contrat_id}", response_model=ContratRead)
async def get_contrat(contrat_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_contrat(contrat_id, db, user)


@router.put("/{contrat_id}", response_model=ContratRead)
async def update_contrat(contrat_id: uuid.UUID, payload: ContratUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.update_contrat(contrat_id, payload, db, user)
