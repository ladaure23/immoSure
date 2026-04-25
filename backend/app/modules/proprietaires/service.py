import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.proprietaire import Proprietaire
from app.models.user import User
from app.schemas.proprietaire import ProprietaireCreate, ProprietaireUpdate


async def list_proprietaires(db: AsyncSession, user: User) -> list[Proprietaire]:
    q = select(Proprietaire).order_by(Proprietaire.created_at.desc())
    if user.role != "admin":
        q = q.where(Proprietaire.agence_id == user.agence_id)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_proprietaire(proprietaire_id: uuid.UUID, db: AsyncSession, user: User) -> Proprietaire:
    result = await db.execute(select(Proprietaire).where(Proprietaire.id == proprietaire_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriétaire introuvable")
    if user.role != "admin" and p.agence_id != user.agence_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return p


async def create_proprietaire(payload: ProprietaireCreate, db: AsyncSession, user: User) -> Proprietaire:
    data = payload.model_dump()
    if user.role != "admin":
        data["agence_id"] = user.agence_id
    p = Proprietaire(**data)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


async def update_proprietaire(proprietaire_id: uuid.UUID, payload: ProprietaireUpdate, db: AsyncSession, user: User) -> Proprietaire:
    p = await get_proprietaire(proprietaire_id, db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    await db.commit()
    await db.refresh(p)
    return p
