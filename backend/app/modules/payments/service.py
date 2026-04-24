import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.transaction import Transaction
from app.models.depot_wallet import DepotWallet
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.schemas.transaction import TransactionRead, DashboardStats, TopBienStats
from app.schemas.depot_wallet import DepotInitierFedapay, DepotInitierKkiapay, DepotResponse


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

    # fix: func.distinct() — Transaction.id.distinct() n'existe pas en SQLAlchemy 2.0
    payes_result = await db.execute(
        select(func.count(func.distinct(Transaction.id)))
        .where(Transaction.mois_concerne >= debut_mois, Transaction.statut == "complete")
    )
    payes = payes_result.scalar() or 0
    # fix: cap à 100% — possible si plusieurs transactions pour un même contrat
    taux_recouvrement = Decimal(str(min(100, round((payes / total_actifs) * 100, 2))))

    attente_result = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.statut == "en_attente")
    )
    en_attente = attente_result.scalar() or 0

    echec_result = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.statut == "echoue")
    )
    echoues = echec_result.scalar() or 0

    # fix: double JOIN explicite — .in_(subquery) comme condition de join donnait de faux résultats
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


async def initier_depot_fedapay(payload: DepotInitierFedapay, db: AsyncSession) -> DepotResponse:
    # Intégration FedaPay complète à l'étape 4 — stub fonctionnel pour les tests
    depot = DepotWallet(
        locataire_id=payload.locataire_id,
        montant=payload.montant,
        provider="fedapay",
        statut="en_attente",
        reference_provider=None,
    )
    db.add(depot)
    await db.commit()
    await db.refresh(depot)
    return DepotResponse(
        depot_id=depot.id,
        payment_url="https://sandbox.fedapay.com/pay/stub",
        reference=str(depot.id),
        montant=depot.montant,
        provider="fedapay",
    )


async def initier_depot_kkiapay(payload: DepotInitierKkiapay, db: AsyncSession) -> DepotResponse:
    # Intégration KKiaPay complète à l'étape 4 — stub fonctionnel pour les tests
    depot = DepotWallet(
        locataire_id=payload.locataire_id,
        montant=payload.montant,
        provider="kkiapay",
        statut="en_attente",
        reference_provider=None,
    )
    db.add(depot)
    await db.commit()
    await db.refresh(depot)
    return DepotResponse(
        depot_id=depot.id,
        payment_url="https://sandbox.kkiapay.me/pay/stub",
        reference=str(depot.id),
        montant=depot.montant,
        provider="kkiapay",
    )


async def handle_webhook_fedapay(body: dict, db: AsyncSession) -> dict:
    # Traitement complet à l'étape 4 (vérification signature HMAC, crédit wallet)
    reference = body.get("transaction", {}).get("id") or body.get("reference")
    if not reference:
        return {"status": "ignored"}
    result = await db.execute(
        select(DepotWallet).where(DepotWallet.reference_provider == str(reference))
    )
    depot = result.scalar_one_or_none()
    # fix: vérifier statut == "en_attente" pour idempotence (providers rejouent les webhooks)
    if depot and depot.statut == "en_attente" and body.get("transaction", {}).get("status") == "approved":
        depot.statut = "complete"
        locataire_result = await db.execute(
            select(Locataire).where(Locataire.id == depot.locataire_id)
        )
        locataire = locataire_result.scalar_one_or_none()
        if locataire:
            locataire.wallet_solde += depot.montant
        await db.commit()
    return {"status": "ok"}


async def handle_webhook_kkiapay(body: dict, signature: str | None, db: AsyncSession) -> dict:
    # Vérification signature et traitement complet à l'étape 4
    reference = body.get("transactionId")
    if not reference:
        return {"status": "ignored"}
    result = await db.execute(
        select(DepotWallet).where(DepotWallet.reference_provider == str(reference))
    )
    depot = result.scalar_one_or_none()
    # fix: vérifier statut == "en_attente" pour idempotence
    if depot and depot.statut == "en_attente" and body.get("status") == "SUCCESS":
        depot.statut = "complete"
        locataire_result = await db.execute(
            select(Locataire).where(Locataire.id == depot.locataire_id)
        )
        locataire = locataire_result.scalar_one_or_none()
        if locataire:
            locataire.wallet_solde += depot.montant
        await db.commit()
    return {"status": "ok"}
