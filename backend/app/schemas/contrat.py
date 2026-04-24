from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, field_validator
from typing import Literal


class ContratBase(BaseModel):
    bien_id: UUID
    locataire_id: UUID
    date_debut: date
    date_fin: date | None = None
    loyer_montant: Decimal
    jour_echeance: int = 1
    statut: Literal["actif", "resilie", "expire"] = "actif"

    @field_validator("jour_echeance")
    @classmethod
    def jour_valide(cls, v: int) -> int:
        if v < 1 or v > 28:
            raise ValueError("Le jour d'échéance doit être entre 1 et 28")
        return v

    @field_validator("loyer_montant")
    @classmethod
    def loyer_positif(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Le loyer doit être positif")
        return v


class ContratCreate(ContratBase):
    pass


class ContratUpdate(BaseModel):
    date_fin: date | None = None
    loyer_montant: Decimal | None = None
    jour_echeance: int | None = None
    statut: Literal["actif", "resilie", "expire"] | None = None

    @field_validator("jour_echeance")
    @classmethod
    def jour_valide(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 28):
            raise ValueError("Le jour d'échéance doit être entre 1 et 28")
        return v

    @field_validator("loyer_montant")
    @classmethod
    def loyer_positif(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Le loyer doit être positif")
        return v


class ContratRead(ContratBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ContratRisque(BaseModel):
    contrat_id: UUID
    locataire_nom: str
    locataire_prenom: str
    locataire_telephone: str
    bien_adresse: str
    loyer_montant: Decimal
    wallet_solde: Decimal
    taux_provisionnement: int
    jours_avant_echeance: int

    model_config = {"from_attributes": True}
