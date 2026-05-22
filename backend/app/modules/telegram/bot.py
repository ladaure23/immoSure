import logging
from decimal import Decimal
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from sqlalchemy import select, and_
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.locataire import Locataire
from app.models.contrat import Contrat
from app.models.location import Location
from app.models.bien import Bien
from app.models.paiement_loyer import PaiementLoyer
from app.modules.payments.split_service import calculer_split
from app.modules.payments.providers.factory import get_provider

logger = logging.getLogger(__name__)

# ConversationHandler states
PHONE_INPUT    = 0   # /start — saisie téléphone
MONTANT_INPUT  = 1   # /payer — saisie montant
PHONE_PAY      = 2   # /payer — saisie numéro mobile money


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(n) -> str:
    return f"{int(n):,}".replace(",", " ") + " FCFA"


async def _get_locataire(chat_id: str) -> Locataire | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        return result.scalar_one_or_none()


# ── /start — liaison compte ───────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Bienvenue sur *ImmoSure* !\n\n"
        "Envoyez votre numéro de téléphone pour lier votre compte locataire.\n"
        "Exemple : `+22997102030`",
        parse_mode="Markdown",
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
                "❌ Numéro non trouvé dans le système.\n"
                "Vérifiez le format (+22997XXXXXX) ou contactez votre agence."
            )
            return PHONE_INPUT
        locataire.telegram_chat_id = chat_id
        await db.commit()
        prenom = locataire.prenom

    await update.message.reply_text(
        f"✅ Compte lié ! Bonjour *{prenom}*.\n\n"
        "Commandes disponibles :\n"
        "/payer — payer votre loyer\n"
        "/paiements — statut du mois\n"
        "/contrats — vos contrats actifs\n"
        "/score — votre score de fiabilité",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Opération annulée.")
    return ConversationHandler.END


# ── /payer — flux de paiement ─────────────────────────────────────────────────

async def payer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = str(update.effective_chat.id)

    async with AsyncSessionLocal() as db:
        loc_result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        locataire = loc_result.scalar_one_or_none()
        if not locataire:
            await update.message.reply_text(
                "Compte non lié. Envoyez /start pour vous enregistrer."
            )
            return ConversationHandler.END

        # Contrats actifs
        rows = await db.execute(
            select(Contrat, Location)
            .join(Location, Contrat.location_id == Location.id)
            .where(
                Contrat.locataire_id == locataire.id,
                Contrat.statut == "actif",
            )
        )
        contrats = rows.all()

    if not contrats:
        await update.message.reply_text("Aucun contrat actif trouvé.")
        return ConversationHandler.END

    if len(contrats) == 1:
        contrat, location = contrats[0]
        context.user_data["contrat_id"] = str(contrat.id)
        context.user_data["loyer_montant"] = int(contrat.loyer_montant)
        context.user_data["location_nom"] = location.nom
        await update.message.reply_text(
            f"🏠 *{location.nom}*\n"
            f"Loyer mensuel : *{_fmt(contrat.loyer_montant)}*\n\n"
            f"Quel montant voulez-vous payer ?\n"
            f"_(Envoyez le montant en chiffres, ex: `{int(contrat.loyer_montant)}`)_",
            parse_mode="Markdown",
        )
        return MONTANT_INPUT

    # Plusieurs contrats → liste numérotée
    context.user_data["contrats_list"] = [
        {"contrat_id": str(c.id), "loyer": int(c.loyer_montant), "nom": l.nom}
        for c, l in contrats
    ]
    lines = [
        f"{i+1}. {l.nom} — {_fmt(c.loyer_montant)}"
        for i, (c, l) in enumerate(contrats)
    ]
    await update.message.reply_text(
        "Vous avez plusieurs contrats. Tapez le numéro :\n\n" + "\n".join(lines)
    )
    return MONTANT_INPUT


async def montant_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().replace(" ", "").replace(" ", "")

    # Si choix de contrat parmi plusieurs
    if "contrats_list" in context.user_data and "contrat_id" not in context.user_data:
        if text.isdigit():
            idx = int(text) - 1
            liste = context.user_data["contrats_list"]
            if 0 <= idx < len(liste):
                chosen = liste[idx]
                context.user_data["contrat_id"] = chosen["contrat_id"]
                context.user_data["loyer_montant"] = chosen["loyer"]
                context.user_data["location_nom"] = chosen["nom"]
                await update.message.reply_text(
                    f"🏠 *{chosen['nom']}*\n"
                    f"Quel montant ? _(loyer : {_fmt(chosen['loyer'])})_",
                    parse_mode="Markdown",
                )
                return MONTANT_INPUT
        await update.message.reply_text("Numéro invalide. Réessayez ou /annuler.")
        return MONTANT_INPUT

    # Saisie du montant
    try:
        montant = int(text)
        if montant <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "❌ Montant invalide. Entrez un nombre entier en FCFA (ex: `120000`).",
            parse_mode="Markdown",
        )
        return MONTANT_INPUT

    loyer = context.user_data.get("loyer_montant", 0)
    if montant > loyer * 2:
        await update.message.reply_text(
            f"⚠️ Montant trop élevé (loyer : {_fmt(loyer)}). Réessayez.",
        )
        return MONTANT_INPUT

    context.user_data["montant"] = montant
    await update.message.reply_text(
        f"Montant : *{_fmt(montant)}*\n\n"
        f"📱 Entrez votre numéro Mobile Money (MTN ou MOOV) :\n"
        f"_(ex: `97102030` ou `66102030`)_",
        parse_mode="Markdown",
    )
    return PHONE_PAY


async def phone_pay_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_raw = update.message.text.strip().replace(" ", "")
    # Normaliser : retirer +229 ou 229 si présent
    phone = phone_raw.replace("+229", "").replace("229", "")

    if len(phone) < 8 or not phone.isdigit():
        await update.message.reply_text(
            "❌ Numéro invalide. Format attendu : `97102030` (8 chiffres).",
            parse_mode="Markdown",
        )
        return PHONE_PAY

    contrat_id = context.user_data["contrat_id"]
    montant    = context.user_data["montant"]
    nom_loc    = context.user_data.get("location_nom", "votre logement")

    await update.message.reply_text("⏳ Génération du lien de paiement…")

    try:
        from app.modules.payments.service import initier_paiement_loyer
        from app.schemas.paiement_loyer import InitierPaiementPayload
        from decimal import Decimal

        payload = InitierPaiementPayload(
            contrat_id=contrat_id,
            montant=Decimal(str(montant)),
            telephone=phone,
        )
        async with AsyncSessionLocal() as db:
            result = await initier_paiement_loyer(payload, db)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Payer maintenant", url=result.payment_url)]
        ])
        await update.message.reply_text(
            f"✅ Lien généré pour *{nom_loc}*\n\n"
            f"Montant : *{_fmt(montant)}*\n"
            f"Cliquez sur le bouton ci-dessous pour payer via FedaPay.\n\n"
            f"_Vous recevrez une confirmation dès que le paiement est validé._",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    except Exception as e:
        logger.error("Erreur paiement Telegram: %s", e)
        await update.message.reply_text(
            f"❌ Erreur lors de la génération du lien : {e}\n"
            "Réessayez ou contactez votre agence."
        )

    # Nettoyer le contexte
    context.user_data.clear()
    return ConversationHandler.END


# ── /score ────────────────────────────────────────────────────────────────────

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        locataire = result.scalar_one_or_none()
    if not locataire:
        await update.message.reply_text("Compte non lié. Utilisez /start.")
        return
    score = locataire.score_fiabilite
    await update.message.reply_text(
        f"📊 Score de fiabilité : *{score}/100*\n"
        f"{'⭐ Excellent' if score >= 80 else '⚠️ À améliorer' if score >= 50 else '🔴 Critique'}",
        parse_mode="Markdown",
    )


# ── /contrats ─────────────────────────────────────────────────────────────────

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
        rows = await db.execute(
            select(Contrat, Location, Bien)
            .join(Location, Contrat.location_id == Location.id)
            .join(Bien, Location.bien_id == Bien.id)
            .where(Contrat.locataire_id == locataire.id, Contrat.statut == "actif")
        )
        lignes = [
            f"🏠 *{location.nom}* — {bien.adresse}\n"
            f"  Loyer : {_fmt(contrat.loyer_montant)}  |  Échéance : J-{contrat.jour_echeance}"
            for contrat, location, bien in rows.all()
        ]
    if not lignes:
        await update.message.reply_text("Aucun contrat actif.")
        return
    await update.message.reply_text(
        "Vos contrats actifs :\n\n" + "\n\n".join(lignes),
        parse_mode="Markdown",
    )


# ── /paiements ────────────────────────────────────────────────────────────────

async def paiements_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    mois = date.today().replace(day=1)

    async with AsyncSessionLocal() as db:
        loc_result = await db.execute(
            select(Locataire).where(Locataire.telegram_chat_id == chat_id)
        )
        locataire = loc_result.scalar_one_or_none()
        if not locataire:
            await update.message.reply_text("Compte non lié. Utilisez /start.")
            return
        rows = await db.execute(
            select(Contrat, Location, PaiementLoyer)
            .join(Location, Contrat.location_id == Location.id)
            .outerjoin(
                PaiementLoyer,
                and_(
                    PaiementLoyer.contrat_id == Contrat.id,
                    PaiementLoyer.periode_debut == mois,
                ),
            )
            .where(Contrat.locataire_id == locataire.id, Contrat.statut == "actif")
        )
        lignes = []
        for contrat, location, pl in rows.all():
            if pl:
                emoji = "✅" if pl.statut == "complet" else "🔶" if pl.statut == "partiel" else "⏳"
                lignes.append(
                    f"{emoji} *{location.nom}*\n"
                    f"  Payé : {_fmt(pl.total_paye)} / {_fmt(pl.loyer_du)}"
                )
            else:
                lignes.append(
                    f"⏳ *{location.nom}*\n"
                    f"  Aucun paiement — dû : {_fmt(contrat.loyer_montant)}"
                )

    if not lignes:
        await update.message.reply_text("Aucun contrat actif.")
        return
    await update.message.reply_text(
        f"Paiements *{mois.strftime('%B %Y')}* :\n\n" + "\n\n".join(lignes),
        parse_mode="Markdown",
    )


# ── Construction de l'application ─────────────────────────────────────────────

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

    payer_conv = ConversationHandler(
        entry_points=[CommandHandler("payer", payer_command)],
        states={
            MONTANT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, montant_input),
                CommandHandler("annuler", cancel_command),
            ],
            PHONE_PAY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, phone_pay_input),
                CommandHandler("annuler", cancel_command),
            ],
        },
        fallbacks=[CommandHandler("annuler", cancel_command)],
    )

    app.add_handler(start_conv)
    app.add_handler(payer_conv)
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("contrats", contrats_command))
    app.add_handler(CommandHandler("paiements", paiements_command))

    return app
