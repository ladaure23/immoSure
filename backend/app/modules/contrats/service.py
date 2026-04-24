import uuid
from calendar import monthrange
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.schemas.contrat import ContratCreate, ContratUpdate, ContratRisque


async def list_contrats(db: AsyncSession) -> list[Contrat]:
    result = await db.execute(select(Contrat).order_by(Contrat.created_at.desc()))
    return list(result.scalars().all())


async def get_contrat(contrat_id: uuid.UUID, db: AsyncSession) -> Contrat:
    result = await db.execute(select(Contrat).where(Contrat.id == contrat_id))
    contrat = result.scalar_one_or_none()
    if not contrat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrat introuvable")
    return contrat


async def create_contrat(payload: ContratCreate, db: AsyncSession) -> Contrat:
    bien_result = await db.execute(select(Bien).where(Bien.id == payload.bien_id))
    bien = bien_result.scalar_one_or_none()
    # fix: empêcher deux contrats actifs sur le même bien
    if bien and bien.statut != "disponible":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce bien est déjà loué")
    contrat = Contrat(**payload.model_dump())
    db.add(contrat)
    if bien:
        bien.statut = "loue"
    await db.commit()
    await db.refresh(contrat)
    return contrat


async def update_contrat(contrat_id: uuid.UUID, payload: ContratUpdate, db: AsyncSession) -> Contrat:
    contrat = await get_contrat(contrat_id, db)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(contrat, field, value)
    if updates.get("statut") in ("resilie", "expire"):
        bien_result = await db.execute(select(Bien).where(Bien.id == contrat.bien_id))
        bien = bien_result.scalar_one_or_none()
        if bien:
            bien.statut = "disponible"
    await db.commit()
    await db.refresh(contrat)
    return contrat


async def get_contrats_a_risque(db: AsyncSession) -> list[ContratRisque]:
    today = date.today()
    result = await db.execute(
        select(Contrat, Locataire, Bien)
        .join(Locataire, Contrat.locataire_id == Locataire.id)
        .join(Bien, Contrat.bien_id == Bien.id)
        .where(Contrat.statut == "actif")
    )
    rows = result.all()

    risques = []
    for contrat, locataire, bien in rows:
        # fix: clamp au dernier jour du mois pour éviter ValueError en février
        max_day = monthrange(today.year, today.month)[1]
        echeance = today.replace(day=min(contrat.jour_echeance, max_day))
        jours = (echeance - today).days
        if jours < 0:
            if today.month == 12:
                next_year, next_month = today.year + 1, 1
            else:
                next_year, next_month = today.year, today.month + 1
            max_day_next = monthrange(next_year, next_month)[1]
            echeance = echeance.replace(year=next_year, month=next_month, day=min(contrat.jour_echeance, max_day_next))
            jours = (echeance - today).days

        if locataire.wallet_solde >= contrat.loyer_montant:
            continue

        taux = min(100, int((locataire.wallet_solde / contrat.loyer_montant) * 100)) if contrat.loyer_montant > 0 else 0

        risques.append(ContratRisque(
            contrat_id=contrat.id,
            locataire_nom=locataire.nom,
            locataire_prenom=locataire.prenom,
            locataire_telephone=locataire.telephone,
            bien_adresse=bien.adresse,
            loyer_montant=contrat.loyer_montant,
            wallet_solde=locataire.wallet_solde,
            taux_provisionnement=taux,
            jours_avant_echeance=jours,
        ))

    return sorted(risques, key=lambda r: r.taux_provisionnement)
