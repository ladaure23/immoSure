"""Initial schema — all tables

Revision ID: 001
Revises:
Create Date: 2026-04-24
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

_uuid_default = sa.text("gen_random_uuid()")

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("raison_sociale", sa.String(200), nullable=False),
        sa.Column("registre_commerce", sa.String(100), unique=True),
        sa.Column("commission_taux", sa.Numeric(5, 2), nullable=False, server_default="8.00"),
        sa.Column("contact_responsable", sa.String(200)),
        sa.Column("telephone", sa.String(20)),
        sa.Column("email", sa.String(200)),
        sa.Column("statut_partenariat", sa.String(50), nullable=False, server_default="actif"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "proprietaires",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("nom", sa.String(100), nullable=False),
        sa.Column("prenom", sa.String(100), nullable=False),
        sa.Column("telephone", sa.String(20), unique=True, nullable=False),
        sa.Column("compte_mobile_money", sa.String(20)),
        sa.Column("operateur_mobile", sa.String(20)),
        sa.Column("whatsapp_id", sa.String(100)),
        sa.Column("telegram_chat_id", sa.String(100)),
        sa.Column("localisation", sa.String(300)),
        sa.Column("agence_id", UUID(as_uuid=True), sa.ForeignKey("agences.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "locataires",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("nom", sa.String(100), nullable=False),
        sa.Column("prenom", sa.String(100), nullable=False),
        sa.Column("telephone", sa.String(20), unique=True, nullable=False),
        sa.Column("telegram_chat_id", sa.String(100)),
        sa.Column("whatsapp_id", sa.String(100)),
        sa.Column("wallet_solde", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("score_fiabilite", sa.Integer, nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="agence"),
        sa.Column("agence_id", UUID(as_uuid=True), sa.ForeignKey("agences.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "biens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("adresse", sa.String(500), nullable=False),
        sa.Column("type_bien", sa.String(50), nullable=False),
        sa.Column("proprietaire_id", UUID(as_uuid=True), sa.ForeignKey("proprietaires.id"), nullable=False),
        sa.Column("agence_id", UUID(as_uuid=True), sa.ForeignKey("agences.id"), nullable=True),
        sa.Column("loyer_mensuel", sa.Numeric(12, 2), nullable=False),
        sa.Column("statut", sa.String(20), nullable=False, server_default="disponible"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "contrats",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("bien_id", UUID(as_uuid=True), sa.ForeignKey("biens.id"), nullable=False),
        sa.Column("locataire_id", UUID(as_uuid=True), sa.ForeignKey("locataires.id"), nullable=False),
        sa.Column("date_debut", sa.Date, nullable=False),
        sa.Column("date_fin", sa.Date, nullable=True),
        sa.Column("loyer_montant", sa.Numeric(12, 2), nullable=False),
        sa.Column("jour_echeance", sa.Integer, nullable=False, server_default="1"),
        sa.Column("statut", sa.String(20), nullable=False, server_default="actif"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("contrat_id", UUID(as_uuid=True), sa.ForeignKey("contrats.id"), nullable=False),
        sa.Column("montant_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("part_proprietaire", sa.Numeric(12, 2), nullable=False),
        sa.Column("part_agence", sa.Numeric(12, 2), nullable=False),
        sa.Column("part_plateforme", sa.Numeric(12, 2), nullable=False),
        sa.Column("part_maintenance", sa.Numeric(12, 2), nullable=False),
        sa.Column("statut", sa.String(20), nullable=False, server_default="en_attente"),
        sa.Column("reference_paiement", sa.String(200)),
        sa.Column("provider", sa.String(50)),
        sa.Column("mois_concerne", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "depots_wallet",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("locataire_id", UUID(as_uuid=True), sa.ForeignKey("locataires.id"), nullable=False),
        sa.Column("montant", sa.Numeric(12, 2), nullable=False),
        sa.Column("reference_provider", sa.String(200)),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("statut", sa.String(20), nullable=False, server_default="en_attente"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("destinataire_id", UUID(as_uuid=True), nullable=False),
        sa.Column("type_destinataire", sa.String(20), nullable=False),
        sa.Column("canal", sa.String(20), nullable=False),
        sa.Column("type_notif", sa.String(20), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("statut_envoi", sa.String(20), nullable=False, server_default="en_attente"),
        sa.Column("contrat_id", UUID(as_uuid=True), sa.ForeignKey("contrats.id"), nullable=True),
        sa.Column("tentatives", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tickets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=_uuid_default),
        sa.Column("contrat_id", UUID(as_uuid=True), sa.ForeignKey("contrats.id"), nullable=False),
        sa.Column("type_ticket", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("statut", sa.String(20), nullable=False, server_default="ouvert"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Index pour les requêtes fréquentes
    op.create_index("ix_contrats_statut", "contrats", ["statut"])
    op.create_index("ix_contrats_locataire_id", "contrats", ["locataire_id"])
    op.create_index("ix_transactions_contrat_id", "transactions", ["contrat_id"])
    op.create_index("ix_transactions_mois_concerne", "transactions", ["mois_concerne"])
    op.create_index("ix_depots_wallet_locataire_id", "depots_wallet", ["locataire_id"])
    op.create_index("ix_notifications_destinataire", "notifications", ["destinataire_id", "type_destinataire"])
    op.create_index("ix_notifications_statut_envoi", "notifications", ["statut_envoi"])


def downgrade() -> None:
    op.drop_index("ix_notifications_statut_envoi")
    op.drop_index("ix_notifications_destinataire")
    op.drop_index("ix_depots_wallet_locataire_id")
    op.drop_index("ix_transactions_mois_concerne")
    op.drop_index("ix_transactions_contrat_id")
    op.drop_index("ix_contrats_locataire_id")
    op.drop_index("ix_contrats_statut")

    op.drop_table("tickets")
    op.drop_table("notifications")
    op.drop_table("depots_wallet")
    op.drop_table("transactions")
    op.drop_table("contrats")
    op.drop_table("biens")
    op.drop_table("users")
    op.drop_table("locataires")
    op.drop_table("proprietaires")
    op.drop_table("agences")
