import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.location import Location
from app.models.bien import Bien
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate


async def list_locations(bien_id: uuid.UUID, db: AsyncSession, user: User) -> list[Location]:
    bien_result = await db.execute(select(Bien).where(Bien.id == bien_id))
    bien = bien_result.scalar_one_or_none()
    if not bien:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bien introuvable")
    if user.role != "admin" and bien.agence_id != user.agence_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    result = await db.execute(
        select(Location).where(Location.bien_id == bien_id).order_by(Location.created_at)
    )
    return list(result.scalars().all())


async def get_location(location_id: uuid.UUID, db: AsyncSession, user: User) -> Location:
    result = await db.execute(
        select(Location).join(Bien, Location.bien_id == Bien.id).where(Location.id == location_id)
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location introuvable")
    bien_result = await db.execute(select(Bien).where(Bien.id == loc.bien_id))
    bien = bien_result.scalar_one_or_none()
    if user.role != "admin" and (not bien or bien.agence_id != user.agence_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return loc


async def create_location(payload: LocationCreate, db: AsyncSession, user: User) -> Location:
    bien_result = await db.execute(select(Bien).where(Bien.id == payload.bien_id))
    bien = bien_result.scalar_one_or_none()
    if not bien:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bien introuvable")
    if user.role != "admin" and bien.agence_id != user.agence_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce bien n'appartient pas à votre agence")
    location = Location(**payload.model_dump())
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def update_location(location_id: uuid.UUID, payload: LocationUpdate, db: AsyncSession, user: User) -> Location:
    loc = await get_location(location_id, db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loc, field, value)
    await db.commit()
    await db.refresh(loc)
    return loc
