import uuid
from calendar import monthrange
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from app.models.contrat import Contrat
from app.models.location import Location
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.models.paiement_loyer import PaiementLoyer
from app.models.user import User
from app.schemas.contrat import ContratCreate, ContratUpdate, ContratRisque


async def list_contrats(db: AsyncSession, user: User) -> list[Contrat]:
    q = (
        select(Contrat)
        .join(Location, Contrat.location_id == Location.id)
        .join(Bien, Location.bien_id == Bien.id)
        .order_by(Contrat.created_at.desc())
    )
    if user.role != "admin":
        q = q.where(Bien.agence_id == user.agence_id)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_contrat(contrat_id: uuid.UUID, db: AsyncSession, user: User) -> Contrat:
    result = await db.execute(select(Contrat).where(Contrat.id == contrat_id))
    contrat = result.scalar_one_or_none()
    if not contrat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrat introuvable")
    if user.role != "admin":
        loc_result = await db.execute(
            select(Location).join(Bien, Location.bien_id == Bien.id)
            .where(Location.id == contrat.location_id, Bien.agence_id == user.agence_id)
        )
        if not loc_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    return contrat


async def create_contrat(payload: ContratCreate, db: AsyncSession, user: User) -> Contrat:
    loc_result = await db.execute(
        select(Location).join(Bien, Location.bien_id == Bien.id)
        .where(Location.id == payload.location_id)
    )
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location introuvable")

    bien_result = await db.execute(select(Bien).where(Bien.id == location.bien_id))
    bien = bien_result.scalar_one_or_none()
    if user.role != "admin" and bien.agence_id != user.agence_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette location n'appartient pas à votre agence")
    if location.statut != "disponible":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette location est déjà louée")

    contrat = Contrat(**payload.model_dump())
    db.add(contrat)
    location.statut = "loue"
    await db.commit()
    await db.refresh(contrat)
    return contrat


async def update_contrat(contrat_id: uuid.UUID, payload: ContratUpdate, db: AsyncSession, user: User) -> Contrat:
    contrat = await get_contrat(contrat_id, db, user)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(contrat, field, value)
    if updates.get("statut") in ("resilie", "expire"):
        loc_result = await db.execute(select(Location).where(Location.id == contrat.location_id))
        location = loc_result.scalar_one_or_none()
        if location:
            location.statut = "disponible"
    await db.commit()
    await db.refresh(contrat)
    return contrat


async def get_contrats_a_risque(db: AsyncSession, user: User) -> list[ContratRisque]:
    today = date.today()
    q = (
        select(Contrat, Locataire, Location, Bien)
        .join(Locataire, Contrat.locataire_id == Locataire.id)
        .join(Location, Contrat.location_id == Location.id)
        .join(Bien, Location.bien_id == Bien.id)
        .where(Contrat.statut == "actif")
    )
    if user.role != "admin":
        q = q.where(Bien.agence_id == user.agence_id)
    result = await db.execute(q)
    rows = result.all()

    mois = today.replace(day=1)

    risques = []
    for contrat, locataire, location, bien in rows:
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

        # Récupérer le PaiementLoyer du mois courant
        pl_result = await db.execute(
            select(PaiementLoyer).where(
                and_(
                    PaiementLoyer.contrat_id == contrat.id,
                    PaiementLoyer.periode_debut == mois,
                )
            )
        )
        pl = pl_result.scalar_one_or_none()

        total_paye = pl.total_paye if pl else Decimal("0")
        loyer = contrat.loyer_montant
        taux = min(100, int((total_paye / loyer) * 100)) if loyer > 0 else 0

        # Exclure les contrats où le loyer est déjà complet
        if pl and pl.statut == "complet":
            continue

        risques.append(ContratRisque(
            contrat_id=contrat.id,
            locataire_nom=locataire.nom,
            locataire_prenom=locataire.prenom,
            locataire_telephone=locataire.telephone,
            bien_adresse=bien.adresse,
            location_nom=location.nom,
            loyer_montant=loyer,
            total_paye=total_paye,
            taux_paiement=taux,
            jours_avant_echeance=jours,
        ))

    return sorted(risques, key=lambda r: r.taux_paiement)
