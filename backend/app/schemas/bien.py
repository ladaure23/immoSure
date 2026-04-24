from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class BienBase(BaseModel):
    adresse: str
    type: Literal["appartement", "villa", "studio", "magasin"]
    proprietaire_id: UUID
    agence_id: UUID | None = None
    loyer_mensuel: Decimal
    statut: Literal["disponible", "loue"] = "disponible"


class BienCreate(BienBase):
    pass


class BienUpdate(BaseModel):
    adresse: str | None = None
    type: Literal["appartement", "villa", "studio", "magasin"] | None = None
    loyer_mensuel: Decimal | None = None
    statut: Literal["disponible", "loue"] | None = None
    agence_id: UUID | None = None


class BienRead(BienBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
