import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.depot_wallet import DepotWallet
from app.schemas.locataire import LocataireCreate, LocataireUpdate, WalletInfo


async def list_locataires(db: AsyncSession) -> list[Locataire]:
    result = await db.execute(select(Locataire).order_by(Locataire.created_at.desc()))
    return list(result.scalars().all())


async def get_locataire(locataire_id: uuid.UUID, db: AsyncSession) -> Locataire:
    result = await db.execute(select(Locataire).where(Locataire.id == locataire_id))
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locataire introuvable")
    return loc


async def create_locataire(payload: LocataireCreate, db: AsyncSession) -> Locataire:
    loc = Locataire(**payload.model_dump())
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


async def update_locataire(locataire_id: uuid.UUID, payload: LocataireUpdate, db: AsyncSession) -> Locataire:
    loc = await get_locataire(locataire_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loc, field, value)
    await db.commit()
    await db.refresh(loc)
    return loc


async def get_wallet(locataire_id: uuid.UUID, db: AsyncSession) -> WalletInfo:
    loc = await get_locataire(locataire_id, db)

    contrat_result = await db.execute(
        select(Contrat)
        .where(Contrat.locataire_id == locataire_id, Contrat.statut == "actif")
        .order_by(Contrat.created_at.desc())
        .limit(1)
    )
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
