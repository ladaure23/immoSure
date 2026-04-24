import re
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, field_validator


class DepotInitierMtn(BaseModel):
    locataire_id: UUID
    montant: Decimal
    telephone: str

    @field_validator("montant")
    @classmethod
    def montant_minimum(cls, v: Decimal) -> Decimal:
        if v < Decimal("500"):
            raise ValueError("Le montant minimum est de 500 FCFA")
        return v

    @field_validator("telephone")
    @classmethod
    def telephone_msisdn(cls, v: str) -> str:
        if not re.match(r"^\+?[0-9]{8,15}$", v):
            raise ValueError("Format téléphone invalide (ex: +22961234567)")
        return v


class DepotWalletRead(BaseModel):
    id: UUID
    locataire_id: UUID
    montant: Decimal
    reference_provider: str | None
    provider: str
    statut: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DepotResponse(BaseModel):
    depot_id: UUID
    payment_url: str | None
    reference: str
    montant: Decimal
    provider: str
