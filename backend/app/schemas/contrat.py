from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, field_validator, model_validator
from typing import Literal

DureeType = Literal["mensuel", "bimestriel", "trimestriel", "semestriel", "annuel", "bail", "indefini"]

_DUREE_MOIS: dict[str, int] = {
    "mensuel": 1,
    "bimestriel": 2,
    "trimestriel": 3,
    "semestriel": 6,
    "annuel": 12,
}


class ContratBase(BaseModel):
    location_id: UUID
    locataire_id: UUID
    date_debut: date
    date_fin: date | None = None
    loyer_montant: Decimal
    jour_echeance: int = 1
    duree_type: DureeType = "indefini"
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

    @model_validator(mode="after")
    def calculer_date_fin(self) -> "ContratBase":
        if self.duree_type in _DUREE_MOIS and self.date_fin is None:
            self.date_fin = self.date_debut + relativedelta(months=_DUREE_MOIS[self.duree_type])
        elif self.duree_type == "bail" and self.date_fin is None:
            raise ValueError("duree_type='bail' requiert une date_fin explicite")
        return self


class ContratCreate(ContratBase):
    pass


class ContratUpdate(BaseModel):
    date_fin: date | None = None
    loyer_montant: Decimal | None = None
    jour_echeance: int | None = None
    duree_type: DureeType | None = None
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
    location_nom: str
    loyer_montant: Decimal
    total_paye: Decimal
    taux_paiement: int
    jours_avant_echeance: int

    model_config = {"from_attributes": True}
