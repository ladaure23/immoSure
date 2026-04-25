import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.bien import Bien
from app.models.user import User
from app.schemas.bien import BienCreate, BienUpdate


async def list_biens(db: AsyncSession, user: User) -> list[Bien]:
    q = select(Bien).order_by(Bien.created_at.desc())
    if user.role != "admin":
        q = q.where(Bien.agence_id == user.agence_id)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_bien(bien_id: uuid.UUID, db: AsyncSession, user: User) -> Bien:
    result = await db.execute(select(Bien).where(Bien.id == bien_id))
    bien = result.scalar_one_or_none()
    if not bien:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bien introuvable")
    if user.role != "admin" and bien.agence_id != user.agence_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return bien


async def create_bien(payload: BienCreate, db: AsyncSession, user: User) -> Bien:
    data = payload.model_dump()
    if user.role != "admin":
        data["agence_id"] = user.agence_id
    bien = Bien(**data)
    db.add(bien)
    await db.commit()
    await db.refresh(bien)
    return bien


async def update_bien(bien_id: uuid.UUID, payload: BienUpdate, db: AsyncSession, user: User) -> Bien:
    bien = await get_bien(bien_id, db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bien, field, value)
    await db.commit()
    await db.refresh(bien)
    return bien
