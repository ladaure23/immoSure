import uuid
import asyncio
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from babel.dates import format_date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transaction import Transaction
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.models.proprietaire import Proprietaire

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)
_TZ_BENIN = ZoneInfo("Africa/Porto-Novo")


async def generate_quittance(transaction_id: uuid.UUID, db: AsyncSession) -> bytes | None:
    result = await db.execute(
        select(Transaction, Contrat, Bien, Locataire, Proprietaire)
        .join(Contrat, Transaction.contrat_id == Contrat.id)
        .join(Bien, Contrat.bien_id == Bien.id)
        .join(Locataire, Contrat.locataire_id == Locataire.id)
        .join(Proprietaire, Bien.proprietaire_id == Proprietaire.id)
        .where(Transaction.id == transaction_id)
    )
    row = result.one_or_none()
    if not row:
        return None

    transaction, contrat, bien, locataire, proprietaire = row

    if transaction.statut != "complete":
        return None

    mois_label = format_date(
        transaction.mois_concerne, format="MMMM yyyy", locale="fr_FR"
    ).upper()

    # Convertir created_at en heure locale Bénin avant rendu
    date_paiement = transaction.created_at.astimezone(_TZ_BENIN).strftime("%d/%m/%Y")

    # Rendu HTML dans le thread async (accès ORM ici)
    html = _env.get_template("quittance.html").render(
        transaction=transaction,
        contrat=contrat,
        bien=bien,
        locataire=locataire,
        proprietaire=proprietaire,
        mois_label=mois_label,
        date_paiement=date_paiement,
    )

    # WeasyPrint est synchrone et CPU-intensif — exécuté dans un thread pour ne pas bloquer l'event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: HTML(string=html, base_url=str(_TEMPLATE_DIR)).write_pdf(),
    )
