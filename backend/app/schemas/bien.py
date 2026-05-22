from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Literal

TypeBien = Literal["immeuble", "villa", "maison", "appartement", "studio", "magasin", "autre"]


class BienBase(BaseModel):
    nom: str | None = None
    adresse: str
    type_bien: TypeBien
    proprietaire_id: UUID
    agence_id: UUID | None = None


class BienCreate(BienBase):
    pass


class BienUpdate(BaseModel):
    nom: str | None = None
    adresse: str | None = None
    type_bien: TypeBien | None = None
    agence_id: UUID | None = None


class BienRead(BienBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
