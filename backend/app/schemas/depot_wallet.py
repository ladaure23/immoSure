from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Literal


class _DepotInitierBase(BaseModel):
    locataire_id: UUID
    montant: Decimal
    telephone: str

    @field_validator("montant")
    @classmethod
    def montant_minimum(cls, v: Decimal) -> Decimal:
        if v < Decimal("500"):
            raise ValueError("Le montant minimum est de 500 FCFA")
        return v


class DepotInitierFedapay(_DepotInitierBase):
    operateur: Literal["MTN", "MOOV"]


class DepotInitierKkiapay(_DepotInitierBase):
    pass


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
    payment_url: str
    reference: str
    montant: Decimal
    provider: str
