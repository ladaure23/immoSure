from datetime import date, timedelta
from loguru import logger
from sqlalchemy import select, and_

from app.database import AsyncSessionLocal
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.modules.payments.split_service import executer_paiements_du_jour, _deja_paye_ce_mois
from app.modules.telegram.notifications import send_notification


async def job_paiements_du_jour() -> None:
    logger.info("Scheduler: déclenchement paiements du jour")
    async with AsyncSessionLocal() as db:
        result = await executer_paiements_du_jour(db)
    logger.info(
        "Scheduler: {traites} contrat(s) traités — {reussis} réussis, {echoues} échoués, {ignores} ignorés",
        traites=result.traites,
        reussis=result.reussis,
        echoues=result.echoues,
        ignores=result.ignores,
    )


async def job_rappels_echeances() -> None:
    today = date.today()
    mois = today.replace(day=1)

    async with AsyncSessionLocal() as db:
        for offset in (7, 3, 1):
            target = today + timedelta(days=offset)

            rows = await db.execute(
                select(Contrat, Locataire, Bien)
                .join(Locataire, Contrat.locataire_id == Locataire.id)
                .join(Bien, Contrat.bien_id == Bien.id)
                .where(
                    and_(
                        Contrat.statut == "actif",
                        Contrat.jour_echeance == target.day,
                    )
                )
            )

            for contrat, locataire, bien in rows.all():
                if await _deja_paye_ce_mois(contrat.id, mois, db):
                    continue  # déjà réglé ce mois — pas de rappel

                # Capturer avant tout await qui pourrait expirer les objets
                chat_id = locataire.telegram_chat_id
                montant = contrat.loyer_montant
                adresse = bien.adresse

                await send_notification(
                    chat_id,
                    f"Rappel : votre loyer de {montant:,.0f} FCFA "
                    f"pour {adresse} est dû dans {offset} jour(s).",
                )
