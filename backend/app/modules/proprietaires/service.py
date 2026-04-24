import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.proprietaire import Proprietaire
from app.schemas.proprietaire import ProprietaireCreate, ProprietaireUpdate


async def list_proprietaires(db: AsyncSession) -> list[Proprietaire]:
    result = await db.execute(select(Proprietaire).order_by(Proprietaire.created_at.desc()))
    return list(result.scalars().all())


async def get_proprietaire(proprietaire_id: uuid.UUID, db: AsyncSession) -> Proprietaire:
    result = await db.execute(select(Proprietaire).where(Proprietaire.id == proprietaire_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriétaire introuvable")
    return p


async def create_proprietaire(payload: ProprietaireCreate, db: AsyncSession) -> Proprietaire:
    p = Proprietaire(**payload.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


async def update_proprietaire(proprietaire_id: uuid.UUID, payload: ProprietaireUpdate, db: AsyncSession) -> Proprietaire:
    p = await get_proprietaire(proprietaire_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    await db.commit()
    await db.refresh(p)
    return p
