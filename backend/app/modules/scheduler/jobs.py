from datetime import date, timedelta
from loguru import logger
from sqlalchemy import select, and_

from app.database import AsyncSessionLocal
from app.models.contrat import Contrat
from app.models.location import Location
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.models.paiement_loyer import PaiementLoyer
from app.modules.telegram.notifications import send_notification


async def _paiement_complet_ce_mois(contrat_id, mois: date, db) -> bool:
    result = await db.execute(
        select(PaiementLoyer).where(
            and_(
                PaiementLoyer.contrat_id == contrat_id,
                PaiementLoyer.periode_debut == mois,
                PaiementLoyer.statut == "complet",
            )
        )
    )
    return result.scalar_one_or_none() is not None


async def job_rappels_echeances() -> None:
    """Envoie des rappels J-7, J-3, J-1 aux locataires dont le loyer n'est pas encore complet."""
    try:
        today = date.today()
        mois = today.replace(day=1)
        notifications: list[tuple[str | None, str]] = []

        async with AsyncSessionLocal() as db:
            for offset in (7, 3, 1):
                target = today + timedelta(days=offset)

                rows = await db.execute(
                    select(Contrat, Locataire, Location, Bien)
                    .join(Locataire, Contrat.locataire_id == Locataire.id)
                    .join(Location, Contrat.location_id == Location.id)
                    .join(Bien, Location.bien_id == Bien.id)
                    .where(
                        and_(
                            Contrat.statut == "actif",
                            Contrat.jour_echeance == target.day,
                        )
                    )
                )

                for contrat, locataire, location, bien in rows.all():
                    if await _paiement_complet_ce_mois(contrat.id, mois, db):
                        continue
                    notifications.append((
                        locataire.telegram_chat_id,
                        f"Rappel : votre loyer de {contrat.loyer_montant:,.0f} FCFA "
                        f"pour {location.nom} ({bien.adresse}) est dû dans {offset} jour(s). "
                        f"Contactez votre agence pour effectuer le paiement.",
                    ))

        for chat_id, message in notifications:
            await send_notification(chat_id, message)

    except Exception:
        logger.exception("Scheduler: erreur dans job_rappels_echeances")


async def job_relances_retard() -> None:
    """Envoie des relances J+3 et J+7 pour les loyers non complets après échéance."""
    try:
        today = date.today()
        mois = today.replace(day=1)
        notifications: list[tuple[str | None, str]] = []

        async with AsyncSessionLocal() as db:
            for offset in (3, 7):
                target = today - timedelta(days=offset)

                rows = await db.execute(
                    select(Contrat, Locataire, Location, Bien)
                    .join(Locataire, Contrat.locataire_id == Locataire.id)
                    .join(Location, Contrat.location_id == Location.id)
                    .join(Bien, Location.bien_id == Bien.id)
                    .where(
                        and_(
                            Contrat.statut == "actif",
                            Contrat.jour_echeance == target.day,
                        )
                    )
                )

                for contrat, locataire, location, bien in rows.all():
                    if await _paiement_complet_ce_mois(contrat.id, mois, db):
                        continue
                    notifications.append((
                        locataire.telegram_chat_id,
                        f"⚠️ Relance : votre loyer de {contrat.loyer_montant:,.0f} FCFA "
                        f"pour {location.nom} ({bien.adresse}) est en retard de {offset} jour(s). "
                        f"Régularisez votre situation auprès de votre agence.",
                    ))

        for chat_id, message in notifications:
            await send_notification(chat_id, message)

    except Exception:
        logger.exception("Scheduler: erreur dans job_relances_retard")
