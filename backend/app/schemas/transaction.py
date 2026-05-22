from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel
from typing import Literal


class TransactionRead(BaseModel):
    id: UUID
    contrat_id: UUID
    montant_total: Decimal
    montant_net: Decimal | None
    frais_fedapay: Decimal | None
    part_proprietaire: Decimal
    part_agence: Decimal
    part_plateforme: Decimal
    statut: Literal["en_attente", "complete", "echoue"]
    fedapay_transaction_id: str | None
    reference_paiement: str | None
    provider: str | None
    mois_concerne: date
    created_at: datetime

    model_config = {"from_attributes": True}


class TopBienStats(BaseModel):
    bien_id: UUID
    adresse: str
    montant_total: Decimal
    nombre_transactions: int


class DashboardStats(BaseModel):
    total_transactions: int
    montant_total_mois: Decimal
    montant_total_annee: Decimal
    taux_recouvrement: Decimal
    transactions_en_attente: int
    transactions_echouees: int
    top_biens: list[TopBienStats]
