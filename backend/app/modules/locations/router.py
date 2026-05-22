import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate, LocationRead
from app.modules.locations import service

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("", response_model=list[LocationRead])
async def list_locations(
    bien_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.list_locations(bien_id, db, user)


@router.post("", response_model=LocationRead, status_code=201)
async def create_location(
    payload: LocationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.create_location(payload, db, user)


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.get_location(location_id, db, user)


@router.put("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: uuid.UUID,
    payload: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.update_location(location_id, payload, db, user)
