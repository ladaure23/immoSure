import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.bien import Bien
from app.schemas.bien import BienCreate, BienUpdate


async def list_biens(db: AsyncSession) -> list[Bien]:
    result = await db.execute(select(Bien).order_by(Bien.created_at.desc()))
    return list(result.scalars().all())


async def get_bien(bien_id: uuid.UUID, db: AsyncSession) -> Bien:
    result = await db.execute(select(Bien).where(Bien.id == bien_id))
    bien = result.scalar_one_or_none()
    if not bien:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bien introuvable")
    return bien


async def create_bien(payload: BienCreate, db: AsyncSession) -> Bien:
    bien = Bien(**payload.model_dump())
    db.add(bien)
    await db.commit()
    await db.refresh(bien)
    return bien


async def update_bien(bien_id: uuid.UUID, payload: BienUpdate, db: AsyncSession) -> Bien:
    bien = await get_bien(bien_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bien, field, value)
    await db.commit()
    await db.refresh(bien)
    return bien
