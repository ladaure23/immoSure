import uuid
import json
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.transaction import Transaction
from app.models.depot_wallet import DepotWallet
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.schemas.transaction import TransactionRead, DashboardStats, TopBienStats
from app.schemas.depot_wallet import DepotInitierMtn, DepotResponse
from app.modules.payments.providers.factory import get_provider
from app.modules.telegram.notifications import send_notification

logger = logging.getLogger(__name__)


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
        .join(Bien, Contrat.bien_id == Bien.id)
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


async def initier_depot_mtn(payload: DepotInitierMtn, db: AsyncSession) -> DepotResponse:
    depot = DepotWallet(
        locataire_id=payload.locataire_id,
        montant=payload.montant,
        provider="mtn",
        statut="en_attente",
        reference_provider=None,
    )
    db.add(depot)
    await db.flush()  # obtenir depot.id avant d'appeler l'API MTN

    provider = get_provider("mtn")
    result = await provider.initier_paiement(
        montant=payload.montant,
        telephone=payload.telephone,
        depot_id=str(depot.id),
    )
    depot.reference_provider = result.reference
    await db.commit()
    await db.refresh(depot)
    return DepotResponse(
        depot_id=depot.id,
        payment_url=result.payment_url or None,
        reference=result.reference,
        montant=depot.montant,
        provider="mtn",
    )


async def handle_webhook_mtn(raw: bytes, db: AsyncSession) -> dict:
    try:
        body = json.loads(raw)
    except Exception:
        return {"status": "ignored"}

    external_id = body.get("externalId")
    mtn_status = body.get("status")

    if not external_id or not mtn_status:
        return {"status": "ignored"}

    try:
        depot_uuid = uuid.UUID(external_id)
    except (ValueError, AttributeError):
        return {"status": "ignored"}

    result = await db.execute(
        select(DepotWallet).where(DepotWallet.id == depot_uuid)
    )
    depot = result.scalar_one_or_none()

    if depot and depot.statut == "en_attente":
        if mtn_status == "SUCCESSFUL":
            if not depot.reference_provider:
                logger.warning("MTN webhook: depot %s sans reference_provider", depot.id)
                return {"status": "rejected"}
            provider = get_provider("mtn")
            confirmed = await provider.verifier_transaction(depot.reference_provider)
            if not confirmed:
                logger.warning("MTN webhook: re-vérification échouée pour depot %s", depot.id)
                return {"status": "rejected"}
            depot.statut = "complete"
            locataire_result = await db.execute(
                select(Locataire).where(Locataire.id == depot.locataire_id)
            )
            locataire = locataire_result.scalar_one_or_none()
            chat_id = None
            montant_credite = depot.montant
            if locataire:
                locataire.wallet_solde += depot.montant
                chat_id = locataire.telegram_chat_id
                logger.info("Wallet crédité: locataire %s +%s XOF (depot %s)", locataire.id, depot.montant, depot.id)
            await db.commit()
            await send_notification(
                chat_id,
                f"Dépôt de {montant_credite:,.0f} FCFA crédité sur votre portefeuille ImmoSure.",
            )
            return {"status": "ok"}
        elif mtn_status == "FAILED":
            depot.statut = "echoue"
            logger.info("Dépôt échoué: depot %s", depot.id)
        await db.commit()
    else:
        logger.info("MTN webhook ignoré: depot %s statut=%s", external_id, depot.statut if depot else "introuvable")

    return {"status": "ok"}
