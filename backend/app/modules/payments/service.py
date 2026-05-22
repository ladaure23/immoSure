import uuid
import json
import logging
from datetime import date
from decimal import Decimal
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status

from app.models.transaction import Transaction
from app.models.paiement_loyer import PaiementLoyer
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.location import Location
from app.models.bien import Bien
from app.models.proprietaire import Proprietaire
from app.models.agence import Agence
from app.schemas.transaction import TransactionRead, DashboardStats, TopBienStats
from app.schemas.paiement_loyer import InitierPaiementPayload, InitierPaiementResponse, PaiementLoyerRead
from app.schemas.proprietaire import InvitationFedapayResult
from app.modules.payments.split_service import calculer_split, TAUX_FEDAPAY
from app.modules.payments.providers.factory import get_provider
from app.modules.telegram.notifications import send_notification
from app.config import settings

logger = logging.getLogger(__name__)


# ── Transactions ──────────────────────────────────────────────────────────────

async def list_transactions(db: AsyncSession) -> list[Transaction]:
    result = await db.execute(select(Transaction).order_by(Transaction.created_at.desc()))
    return list(result.scalars().all())


async def get_transaction(transaction_id: uuid.UUID, db: AsyncSession) -> Transaction:
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction introuvable")
    return t


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    today = date.today()
    debut_mois = today.replace(day=1)
    debut_annee = today.replace(month=1, day=1)

    total_result = await db.execute(select(func.count(Transaction.id)))
    total = total_result.scalar() or 0

    mois_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.montant_total), Decimal("0")))
        .where(Transaction.mois_concerne >= debut_mois, Transaction.statut == "complete")
    )
    montant_mois = mois_result.scalar() or Decimal("0")

    annee_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.montant_total), Decimal("0")))
        .where(Transaction.mois_concerne >= debut_annee, Transaction.statut == "complete")
    )
    montant_annee = annee_result.scalar() or Decimal("0")

    actifs_result = await db.execute(
        select(func.count(Contrat.id)).where(Contrat.statut == "actif")
    )
    total_actifs = actifs_result.scalar() or 1

    payes_result = await db.execute(
        select(func.count(func.distinct(Transaction.id)))
        .where(Transaction.mois_concerne >= debut_mois, Transaction.statut == "complete")
    )
    payes = payes_result.scalar() or 0
    taux_recouvrement = Decimal(str(min(100, round((payes / total_actifs) * 100, 2))))

    attente_result = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.statut == "en_attente")
    )
    en_attente = attente_result.scalar() or 0

    echec_result = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.statut == "echoue")
    )
    echoues = echec_result.scalar() or 0

    top_result = await db.execute(
        select(
            Bien.id,
            Bien.adresse,
            func.sum(Transaction.montant_total).label("montant_total"),
            func.count(Transaction.id).label("nombre_transactions"),
        )
        .join(Contrat, Transaction.contrat_id == Contrat.id)
        .join(Location, Contrat.location_id == Location.id)
        .join(Bien, Location.bien_id == Bien.id)
        .where(Transaction.statut == "complete")
        .group_by(Bien.id, Bien.adresse)
        .order_by(func.sum(Transaction.montant_total).desc())
        .limit(5)
    )
    top_biens = [
        TopBienStats(bien_id=row.id, adresse=row.adresse, montant_total=row.montant_total, nombre_transactions=row.nombre_transactions)
        for row in top_result.all()
    ]

    return DashboardStats(
        total_transactions=total,
        montant_total_mois=montant_mois,
        montant_total_annee=montant_annee,
        taux_recouvrement=taux_recouvrement,
        transactions_en_attente=en_attente,
        transactions_echouees=echoues,
        top_biens=top_biens,
    )


# ── Paiements loyer ───────────────────────────────────────────────────────────

async def _get_periode(contrat: Contrat) -> tuple[date, date]:
    """Retourne (periode_debut, periode_fin) pour le mois courant."""
    today = date.today()
    debut = today.replace(day=1)
    if debut.month == 12:
        fin = debut.replace(year=debut.year + 1, month=1, day=1)
    else:
        fin = debut.replace(month=debut.month + 1, day=1)
    return debut, fin


async def initier_paiement_loyer(payload: InitierPaiementPayload, db: AsyncSession) -> InitierPaiementResponse:
    # Charger le contrat et ses relations
    result = await db.execute(
        select(Contrat, Location, Bien, Proprietaire, Locataire)
        .join(Location, Contrat.location_id == Location.id)
        .join(Bien, Location.bien_id == Bien.id)
        .join(Proprietaire, Bien.proprietaire_id == Proprietaire.id)
        .join(Locataire, Contrat.locataire_id == Locataire.id)
        .where(Contrat.id == payload.contrat_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Contrat introuvable")

    contrat, location, bien, proprietaire, locataire = row

    if contrat.statut != "actif":
        raise HTTPException(status_code=400, detail="Contrat non actif")

    # Split possible uniquement si le propriétaire a accepté l'invitation FedaPay
    # Sinon le paiement passe sans split (tout sur le compte principal)

    # Charger l'agence si applicable
    ref_agence: str | None = None
    has_agence = bien.agence_id is not None
    if has_agence:
        agence_result = await db.execute(select(Agence).where(Agence.id == bien.agence_id))
        agence = agence_result.scalar_one_or_none()
        if agence:
            ref_agence = agence.fedapay_sub_account_ref

    # Déterminer l'opérateur depuis le numéro de téléphone (heuristique Bénin)
    operateur: Literal["mtn", "moov"] = _detecter_operateur(payload.telephone)

    # Calculer le split
    split = calculer_split(
        montant_brut=payload.montant,
        operateur=operateur,
        has_agence=has_agence and ref_agence is not None,
        ref_proprietaire=proprietaire.fedapay_sub_account_ref,
        ref_agence=ref_agence,
        ref_plateforme=settings.fedapay_platform_account_ref or None,
    )

    # Période concernée
    periode_debut, periode_fin = await _get_periode(contrat)

    # Upsert PaiementLoyer pour la période
    pl_result = await db.execute(
        select(PaiementLoyer).where(
            and_(
                PaiementLoyer.contrat_id == contrat.id,
                PaiementLoyer.periode_debut == periode_debut,
            )
        )
    )
    paiement_loyer = pl_result.scalar_one_or_none()
    if not paiement_loyer:
        paiement_loyer = PaiementLoyer(
            contrat_id=contrat.id,
            periode_debut=periode_debut,
            periode_fin=periode_fin,
            loyer_du=contrat.loyer_montant,
            total_paye=Decimal("0"),
            statut="en_attente",
        )
        db.add(paiement_loyer)
        await db.flush()

    # Initier le paiement FedaPay
    provider = get_provider()
    description = f"Loyer {location.nom} — {periode_debut.strftime('%B %Y')}"
    init_result = await provider.initier_paiement(
        montant=payload.montant,
        telephone=payload.telephone,
        description=description,
        splits=split["splits"],
        metadata={
            "contrat_id": str(contrat.id),
            "paiement_loyer_id": str(paiement_loyer.id),
            "periode": str(periode_debut),
        },
    )

    await db.commit()

    return InitierPaiementResponse(
        paiement_loyer_id=paiement_loyer.id,
        fedapay_transaction_id=init_result.reference,
        payment_url=init_result.payment_url,
        montant=payload.montant,
        periode_debut=periode_debut,
        periode_fin=periode_fin,
    )


async def get_paiements_loyer(contrat_id: uuid.UUID, db: AsyncSession) -> list[PaiementLoyer]:
    result = await db.execute(
        select(PaiementLoyer)
        .where(PaiementLoyer.contrat_id == contrat_id)
        .order_by(PaiementLoyer.periode_debut.desc())
    )
    return list(result.scalars().all())


# ── Webhook FedaPay ───────────────────────────────────────────────────────────

async def handle_webhook_fedapay(raw: bytes, signature: str | None, db: AsyncSession) -> dict:
    provider = get_provider()
    if not provider.verifier_signature_webhook(raw, signature):
        logger.warning("FedaPay webhook: signature invalide | reçue=%r", signature)
        return {"status": "rejected"}

    try:
        body = json.loads(raw)
    except Exception:
        return {"status": "ignored"}

    event_name = body.get("event", {}).get("name", "")
    entity = body.get("entity", {})

    if event_name != "transaction.approved":
        return {"status": "ignored"}

    fedapay_transaction_id = str(entity.get("id", ""))
    montant_total = Decimal(str(entity.get("amount", 0)))
    commission = Decimal(str(entity.get("commission", 0)))
    montant_net = montant_total - commission

    metadata = entity.get("custom_metadata", {})
    contrat_id_str = metadata.get("contrat_id")
    paiement_loyer_id_str = metadata.get("paiement_loyer_id")

    if not contrat_id_str:
        logger.warning("FedaPay webhook: contrat_id absent des métadonnées")
        return {"status": "ignored"}

    try:
        contrat_id = uuid.UUID(contrat_id_str)
    except ValueError:
        return {"status": "ignored"}

    # Charger le contrat
    contrat_result = await db.execute(select(Contrat).where(Contrat.id == contrat_id))
    contrat = contrat_result.scalar_one_or_none()
    if not contrat:
        return {"status": "ignored"}

    # Récupérer les parts réelles depuis la réponse FedaPay
    commissions_list = entity.get("sub_accounts_commissions", [])
    part_proprietaire = Decimal("0")
    part_agence = Decimal("0")

    # Charger bien pour retrouver proprio/agence et recalculer si besoin
    loc_result = await db.execute(
        select(Location, Bien, Proprietaire)
        .join(Bien, Location.bien_id == Bien.id)
        .join(Proprietaire, Bien.proprietaire_id == Proprietaire.id)
        .where(Location.id == contrat.location_id)
    )
    loc_row = loc_result.one_or_none()
    if loc_row:
        location, bien, proprietaire = loc_row
        for c in commissions_list:
            if c.get("reference") == proprietaire.fedapay_sub_account_ref:
                part_proprietaire = Decimal(str(c.get("amount", 0)))
            else:
                part_agence += Decimal(str(c.get("amount", 0)))

    part_plateforme = montant_net - part_proprietaire - part_agence

    # Créer la Transaction
    mois = date.today().replace(day=1)
    transaction = Transaction(
        contrat_id=contrat_id,
        montant_total=montant_total,
        montant_net=montant_net,
        frais_fedapay=commission,
        part_proprietaire=part_proprietaire,
        part_agence=part_agence,
        part_plateforme=part_plateforme,
        statut="complete",
        fedapay_transaction_id=fedapay_transaction_id,
        provider="fedapay",
        mois_concerne=mois,
    )
    db.add(transaction)

    # Mettre à jour PaiementLoyer
    if paiement_loyer_id_str:
        try:
            pl_id = uuid.UUID(paiement_loyer_id_str)
            pl_result = await db.execute(select(PaiementLoyer).where(PaiementLoyer.id == pl_id))
            pl = pl_result.scalar_one_or_none()
            if pl:
                pl.total_paye += montant_total
                if pl.total_paye >= pl.loyer_du:
                    pl.statut = "complet"
                    # Améliorer score fiabilité
                    loc_result2 = await db.execute(select(Locataire).where(Locataire.id == contrat.locataire_id))
                    locataire = loc_result2.scalar_one_or_none()
                    if locataire:
                        locataire.score_fiabilite = min(100, locataire.score_fiabilite + 1)
                else:
                    pl.statut = "partiel"
        except ValueError:
            pass

    await db.commit()

    # Notifications
    if loc_row:
        _, _, proprietaire = loc_row
        loc_result3 = await db.execute(select(Locataire).where(Locataire.id == contrat.locataire_id))
        locataire = loc_result3.scalar_one_or_none()
        if locataire:
            await send_notification(
                locataire.telegram_chat_id,
                f"Paiement de {montant_total:,.0f} FCFA confirmé pour {location.nom}.",
            )

    logger.info("FedaPay webhook traité: transaction %s, contrat %s, montant %s", fedapay_transaction_id, contrat_id, montant_total)
    return {"status": "ok"}


# ── Invitations FedaPay ───────────────────────────────────────────────────────

async def inviter_proprietaire_fedapay(proprietaire_id: uuid.UUID, db: AsyncSession) -> InvitationFedapayResult:
    result = await db.execute(select(Proprietaire).where(Proprietaire.id == proprietaire_id))
    proprio = result.scalar_one_or_none()
    if not proprio:
        raise HTTPException(status_code=404, detail="Propriétaire introuvable")
    if not proprio.email:
        raise HTTPException(status_code=400, detail="Email du propriétaire requis pour l'invitation FedaPay")

    provider = get_provider()
    try:
        ref = await provider.inviter_sous_compte(
            email=proprio.email,
            full_name=f"{proprio.prenom} {proprio.nom}",
        )
        proprio.fedapay_sub_account_ref = ref
        await db.commit()
        return InvitationFedapayResult(success=True, message="Invitation envoyée", fedapay_ref=ref)
    except HTTPException as e:
        return InvitationFedapayResult(success=False, message=str(e.detail))


async def inviter_agence_fedapay(agence_id: uuid.UUID, db: AsyncSession) -> InvitationFedapayResult:
    result = await db.execute(select(Agence).where(Agence.id == agence_id))
    agence = result.scalar_one_or_none()
    if not agence:
        raise HTTPException(status_code=404, detail="Agence introuvable")
    if not agence.email:
        raise HTTPException(status_code=400, detail="Email de l'agence requis pour l'invitation FedaPay")

    provider = get_provider()
    try:
        ref = await provider.inviter_sous_compte(
            email=agence.email,
            full_name=agence.raison_sociale,
        )
        agence.fedapay_sub_account_ref = ref
        await db.commit()
        return InvitationFedapayResult(success=True, message="Invitation envoyée", fedapay_ref=ref)
    except HTTPException as e:
        return InvitationFedapayResult(success=False, message=str(e.detail))


# ── Helper ────────────────────────────────────────────────────────────────────

def _detecter_operateur(telephone: str) -> Literal["mtn", "moov"]:
    """Heuristique Bénin : MTN commence par 96/97, MOOV par 94/95/96 selon préfixe."""
    t = telephone.replace(" ", "").replace("+229", "").replace("229", "")
    if t.startswith(("96", "97", "61", "62", "63", "64", "65", "66", "67")):
        return "mtn"
    return "moov"
