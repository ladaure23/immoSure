import uuid
from pathlib import Path

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

    html = _env.get_template("quittance.html").render(
        transaction=transaction,
        contrat=contrat,
        bien=bien,
        locataire=locataire,
        proprietaire=proprietaire,
        mois_label=mois_label,
    )

    return HTML(string=html, base_url=str(_TEMPLATE_DIR)).write_pdf()
