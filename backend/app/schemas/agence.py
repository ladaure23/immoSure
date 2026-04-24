from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal


class AgenceBase(BaseModel):
    raison_sociale: str
    registre_commerce: str | None = None
    commission_taux: Decimal = Decimal("8.00")
    contact_responsable: str | None = None
    telephone: str | None = None
    email: EmailStr | None = None
    statut_partenariat: str = "actif"

    @field_validator("commission_taux")
    @classmethod
    def taux_valide(cls, v: Decimal) -> Decimal:
        if v < 0 or v > 100:
            raise ValueError("Le taux de commission doit être entre 0 et 100")
        return v


class AgenceCreate(AgenceBase):
    pass


class AgenceUpdate(BaseModel):
    raison_sociale: str | None = None
    registre_commerce: str | None = None
    commission_taux: Decimal | None = None
    contact_responsable: str | None = None
    telephone: str | None = None
    email: EmailStr | None = None
    statut_partenariat: str | None = None

    @field_validator("commission_taux")
    @classmethod
    def taux_valide(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Le taux de commission doit être entre 0 et 100")
        return v


class AgenceRead(AgenceBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
