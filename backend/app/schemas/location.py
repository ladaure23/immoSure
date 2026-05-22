from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Literal

TypeLocation = Literal["appartement", "studio", "chambre", "villa", "magasin", "bureau", "autre"]


class LocationBase(BaseModel):
    bien_id: UUID
    nom: str
    type_location: TypeLocation
    surface_m2: Decimal | None = None
    loyer_mensuel: Decimal
    statut: Literal["disponible", "loue"] = "disponible"

    @field_validator("loyer_mensuel")
    @classmethod
    def loyer_positif(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Le loyer doit être positif")
        return v


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    nom: str | None = None
    type_location: TypeLocation | None = None
    surface_m2: Decimal | None = None
    loyer_mensuel: Decimal | None = None
    statut: Literal["disponible", "loue"] | None = None

    @field_validator("loyer_mensuel")
    @classmethod
    def loyer_positif(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Le loyer doit être positif")
        return v


class LocationRead(LocationBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
