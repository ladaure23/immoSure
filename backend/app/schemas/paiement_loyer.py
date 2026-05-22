from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel
from typing import Literal


class PaiementLoyerRead(BaseModel):
    id: UUID
    contrat_id: UUID
    periode_debut: date
    periode_fin: date
    loyer_du: Decimal
    total_paye: Decimal
    statut: Literal["en_attente", "partiel", "complet"]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InitierPaiementPayload(BaseModel):
    contrat_id: UUID
    montant: Decimal
    telephone: str  # numéro mobile money du locataire


class InitierPaiementResponse(BaseModel):
    paiement_loyer_id: UUID
    fedapay_transaction_id: str
    payment_url: str
    montant: Decimal
    periode_debut: date
    periode_fin: date
