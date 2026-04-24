import logging
from decimal import Decimal
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from sqlalchemy import select
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.modules.payments.split_service import executer_paiement_contrat

logger = logging.getLogger(__name__)

PHONE_INPUT = 0  # état ConversationHandler /start


async def _get_locataire(chat_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        return result.scalar_one_or_none()


# --- /start ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bienvenue sur ImmoSure!\n\n"
        "Envoyez votre numéro de téléphone pour lier votre compte (ex: +22961234567)."
    )
    return PHONE_INPUT


async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text.strip()
    chat_id = str(update.effective_chat.id)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Locataire).where(Locataire.telephone == phone)
        )
        locataire = result.scalar_one_or_none()
        if not locataire:
            await update.message.reply_text(
                "Numéro non trouvé. Vérifiez et réessayez, ou envoyez /annuler."
            )
            return PHONE_INPUT
        locataire.telegram_chat_id = chat_id
        await db.commit()
        prenom = locataire.prenom

    await update.message.reply_text(
        f"Compte lié ! Bonjour {prenom}.\n"
        "Commandes disponibles :\n"
        "/solde — voir votre portefeuille\n"
        "/payer — payer le loyer du mois\n"
        "/contrats — vos contrats actifs"
    )
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enregistrement annulé.")
    return ConversationHandler.END


# --- /solde ---

async def solde_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        locataire = result.scalar_one_or_none()

    if not locataire:
        await update.message.reply_text("Compte non lié. Utilisez /start pour vous enregistrer.")
        return

    await update.message.reply_text(
        f"Solde portefeuille : {locataire.wallet_solde:,.0f} FCFA\n"
        f"Score de fiabilité : {locataire.score_fiabilite}/100"
    )


# --- /contrats ---

async def contrats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    async with AsyncSessionLocal() as db:
        loc_result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        locataire = loc_result.scalar_one_or_none()
        if not locataire:
            await update.message.reply_text("Compte non lié. Utilisez /start.")
            return

        contrats_result = await db.execute(
            select(Contrat, Bien)
            .join(Bien, Contrat.bien_id == Bien.id)
            .where(Contrat.locataire_id == locataire.id, Contrat.statut == "actif")
        )
        rows = contrats_result.all()

    if not rows:
        await update.message.reply_text("Aucun contrat actif.")
        return

    lignes = []
    for contrat, bien in rows:
        lignes.append(
            f"- {bien.adresse}\n"
            f"  Loyer : {contrat.loyer_montant:,.0f} FCFA  |  Échéance : J-{contrat.jour_echeance}"
        )
    await update.message.reply_text("Vos contrats actifs :\n\n" + "\n\n".join(lignes))


# --- /payer ---

async def payer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    async with AsyncSessionLocal() as db:
        loc_result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        locataire = loc_result.scalar_one_or_none()
        if not locataire:
            await update.message.reply_text("Compte non lié. Utilisez /start.")
            return

        contrats_result = await db.execute(
            select(Contrat).where(
                Contrat.locataire_id == locataire.id,
                Contrat.statut == "actif",
            )
        )
        contrats = list(contrats_result.scalars().all())

    if not contrats:
        await update.message.reply_text("Aucun contrat actif à payer.")
        return

    await update.message.reply_text(
        f"Traitement de {len(contrats)} contrat(s) en cours..."
    )

    reussis, echoues = 0, 0
    for contrat in contrats:
        async with AsyncSessionLocal() as db:
            resultat = await executer_paiement_contrat(contrat.id, db)
        if resultat.statut == "complete":
            reussis += 1
        elif resultat.statut == "echoue":
            echoues += 1

    await update.message.reply_text(
        f"Paiements terminés :\n"
        f"  Réussis : {reussis}\n"
        f"  Échoués : {echoues}\n\n"
        f"Utilisez /solde pour voir votre nouveau solde."
    )


# --- Construction de l'application ---

def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()

    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            PHONE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone),
                CommandHandler("annuler", cancel_command),
            ]
        },
        fallbacks=[CommandHandler("annuler", cancel_command)],
    )

    app.add_handler(start_conv)
    app.add_handler(CommandHandler("solde", solde_command))
    app.add_handler(CommandHandler("contrats", contrats_command))
    app.add_handler(CommandHandler("payer", payer_command))

    return app
