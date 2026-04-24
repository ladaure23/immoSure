from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Literal

TypeBien = Literal["appartement", "villa", "studio", "magasin"]


class BienBase(BaseModel):
    adresse: str
    type_bien: TypeBien
    proprietaire_id: UUID
    agence_id: UUID | None = None
    loyer_mensuel: Decimal
    statut: Literal["disponible", "loue"] = "disponible"

    @field_validator("loyer_mensuel")
    @classmethod
    def loyer_positif(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Le loyer doit être positif")
        return v


class BienCreate(BienBase):
    pass


class BienUpdate(BaseModel):
    adresse: str | None = None
    type_bien: TypeBien | None = None
    loyer_mensuel: Decimal | None = None
    statut: Literal["disponible", "loue"] | None = None
    agence_id: UUID | None = None

    @field_validator("loyer_mensuel")
    @classmethod
    def loyer_positif(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Le loyer doit être positif")
        return v


class BienRead(BienBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
