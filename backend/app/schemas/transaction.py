from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel
from typing import Literal


class TransactionRead(BaseModel):
    id: UUID
    contrat_id: UUID
    montant_total: Decimal
    part_proprietaire: Decimal
    part_agence: Decimal
    part_plateforme: Decimal
    part_maintenance: Decimal
    statut: Literal["en_attente", "complete", "echoue"]
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
    taux_recouvrement: Decimal  # % contrats payés ce mois
    transactions_en_attente: int
    transactions_echouees: int
    top_biens: list[TopBienStats]


class PaiementResultat(BaseModel):
    contrat_id: UUID
    statut: Literal["complete", "echoue", "ignore"]
    montant: Decimal | None = None
    raison: str | None = None


class BatchPaiementResultat(BaseModel):
    traites: int
    reussis: int
    echoues: int
    ignores: int
    details: list[PaiementResultat]
