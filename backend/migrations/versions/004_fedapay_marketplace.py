"""Fedapay marketplace — supprimer wallet, ajouter refs fedapay, créer paiement_loyer

Revision ID: 004
Revises: 003
"""
from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── locataires : supprimer wallet_solde ───────────────────────────────────
    op.drop_column("locataires", "wallet_solde")

    # ── proprietaires : ajouter email + fedapay ref ───────────────────────────
    op.add_column("proprietaires", sa.Column("email", sa.String(200), nullable=True))
    op.add_column("proprietaires", sa.Column("fedapay_sub_account_ref", sa.String(100), nullable=True))

    # ── agences : ajouter fedapay ref ─────────────────────────────────────────
    op.add_column("agences", sa.Column("fedapay_sub_account_ref", sa.String(100), nullable=True))

    # ── transactions : supprimer part_maintenance, ajouter nouveaux champs ────
    op.drop_column("transactions", "part_maintenance")
    op.add_column("transactions", sa.Column("fedapay_transaction_id", sa.String(100), nullable=True))
    op.add_column("transactions", sa.Column("montant_net", sa.Numeric(12, 2), nullable=True))
    op.add_column("transactions", sa.Column("frais_fedapay", sa.Numeric(12, 2), nullable=True))

    # ── paiement_loyer : nouvelle table ───────────────────────────────────────
    op.create_table(
        "paiement_loyer",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contrat_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("contrats.id"), nullable=False),
        sa.Column("periode_debut", sa.Date, nullable=False),
        sa.Column("periode_fin", sa.Date, nullable=False),
        sa.Column("loyer_du", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_paye", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("statut", sa.String(20), nullable=False, server_default="en_attente"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_paiement_loyer_contrat_periode", "paiement_loyer", ["contrat_id", "periode_debut"])

    # depot_wallet n'existait pas en base — rien à dropper


def downgrade() -> None:
    op.create_table(
        "depot_wallet",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("locataire_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("montant", sa.Numeric(12, 2), nullable=False),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("statut", sa.String(20), nullable=False, server_default="en_attente"),
        sa.Column("reference_provider", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.drop_index("ix_paiement_loyer_contrat_periode", "paiement_loyer")
    op.drop_table("paiement_loyer")
    op.drop_column("transactions", "frais_fedapay")
    op.drop_column("transactions", "montant_net")
    op.drop_column("transactions", "fedapay_transaction_id")
    op.add_column("transactions", sa.Column("part_maintenance", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.drop_column("agences", "fedapay_sub_account_ref")
    op.drop_column("proprietaires", "fedapay_sub_account_ref")
    op.drop_column("proprietaires", "email")
    op.add_column("locataires", sa.Column("wallet_solde", sa.Numeric(12, 2), nullable=False, server_default="0"))
