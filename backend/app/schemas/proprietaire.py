from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class ProprietaireBase(BaseModel):
    nom: str
    prenom: str
    telephone: str
    compte_mobile_money: str | None = None
    operateur_mobile: Literal["MTN", "MOOV", "WAVE"] | None = None
    whatsapp_id: str | None = None
    telegram_chat_id: str | None = None
    localisation: str | None = None
    agence_id: UUID | None = None


class ProprietaireCreate(ProprietaireBase):
    pass


class ProprietaireUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    telephone: str | None = None
    compte_mobile_money: str | None = None
    operateur_mobile: Literal["MTN", "MOOV", "WAVE"] | None = None
    whatsapp_id: str | None = None
    telegram_chat_id: str | None = None
    localisation: str | None = None
    agence_id: UUID | None = None


class ProprietaireRead(ProprietaireBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
