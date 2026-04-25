import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.models.depot_wallet import DepotWallet
from app.models.user import User
from app.schemas.locataire import LocataireCreate, LocataireUpdate, WalletInfo


async def list_locataires(db: AsyncSession, user: User) -> list[Locataire]:
    if user.role == "admin":
        result = await db.execute(select(Locataire).order_by(Locataire.created_at.desc()))
        return list(result.scalars().all())
    # LEFT JOIN : locataires liés à cette agence OU sans contrat (nouvellement créés)
    result = await db.execute(
        select(Locataire)
        .outerjoin(Contrat, Contrat.locataire_id == Locataire.id)
        .outerjoin(Bien, Contrat.bien_id == Bien.id)
        .where((Bien.agence_id == user.agence_id) | (Contrat.id == None))
        .distinct()
        .order_by(Locataire.created_at.desc())
    )
    return list(result.scalars().all())


async def get_locataire(locataire_id: uuid.UUID, db: AsyncSession, user: User) -> Locataire:
    result = await db.execute(select(Locataire).where(Locataire.id == locataire_id))
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locataire introuvable")
    if user.role != "admin":
        access = await db.execute(
            select(Contrat)
            .join(Bien, Contrat.bien_id == Bien.id)
            .where(Contrat.locataire_id == locataire_id, Bien.agence_id == user.agence_id)
            .limit(1)
        )
        if not access.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return loc


async def create_locataire(payload: LocataireCreate, db: AsyncSession, user: User) -> Locataire:
    loc = Locataire(**payload.model_dump())
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


async def update_locataire(locataire_id: uuid.UUID, payload: LocataireUpdate, db: AsyncSession, user: User) -> Locataire:
    loc = await get_locataire(locataire_id, db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loc, field, value)
    await db.commit()
    await db.refresh(loc)
    return loc


async def get_wallet(locataire_id: uuid.UUID, db: AsyncSession, user: User) -> WalletInfo:
    loc = await get_locataire(locataire_id, db, user)

    q = (
        select(Contrat)
        .join(Bien, Contrat.bien_id == Bien.id)
        .where(Contrat.locataire_id == locataire_id, Contrat.statut == "actif")
    )
    if user.role != "admin":
        q = q.where(Bien.agence_id == user.agence_id)
    contrat_result = await db.execute(q.order_by(Contrat.created_at.desc()).limit(1))
    contrat = contrat_result.scalar_one_or_none()
    loyer = contrat.loyer_montant if contrat else None

    taux = 0
    if loyer and loyer > 0:
        taux = min(100, int((loc.wallet_solde / loyer) * 100))

    depots_result = await db.execute(
        select(DepotWallet)
        .where(DepotWallet.locataire_id == locataire_id)
        .order_by(DepotWallet.created_at.desc())
        .limit(20)
    )
    historique = list(depots_result.scalars().all())

    return WalletInfo(
        locataire_id=loc.id,
        solde=loc.wallet_solde,
        loyer_mensuel=loyer,
        taux_provisionnement=taux,
        historique=historique,
    )
