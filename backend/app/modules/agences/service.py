import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.agence import Agence
from app.schemas.agence import AgenceCreate, AgenceUpdate


async def list_agences(db: AsyncSession) -> list[Agence]:
    result = await db.execute(select(Agence).order_by(Agence.created_at.desc()))
    return list(result.scalars().all())


async def get_agence(agence_id: uuid.UUID, db: AsyncSession) -> Agence:
    result = await db.execute(select(Agence).where(Agence.id == agence_id))
    agence = result.scalar_one_or_none()
    if not agence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agence introuvable")
    return agence


async def create_agence(payload: AgenceCreate, db: AsyncSession) -> Agence:
    agence = Agence(**payload.model_dump())
    db.add(agence)
    await db.commit()
    await db.refresh(agence)
    return agence


async def update_agence(agence_id: uuid.UUID, payload: AgenceUpdate, db: AsyncSession) -> Agence:
    agence = await get_agence(agence_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(agence, field, value)
    await db.commit()
    await db.refresh(agence)
    return agence
