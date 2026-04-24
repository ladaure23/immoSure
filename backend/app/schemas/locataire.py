from __future__ import annotations
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.depot_wallet import DepotWalletRead


class LocataireBase(BaseModel):
    nom: str
    prenom: str
    telephone: str
    telegram_chat_id: str | None = None
    whatsapp_id: str | None = None


class LocataireCreate(LocataireBase):
    pass


class LocataireUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    telephone: str | None = None
    telegram_chat_id: str | None = None
    whatsapp_id: str | None = None


class LocataireRead(LocataireBase):
    id: UUID
    wallet_solde: Decimal
    score_fiabilite: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletInfo(BaseModel):
    locataire_id: UUID
    solde: Decimal
    loyer_mensuel: Decimal | None
    taux_provisionnement: int

    @field_validator("taux_provisionnement")
    @classmethod
    def taux_borne(cls, v: int) -> int:
        return max(0, min(100, v))

    historique: list[DepotWalletRead]

    model_config = {"from_attributes": True}
