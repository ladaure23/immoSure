from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


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
    score_fiabilite: int
    created_at: datetime

    model_config = {"from_attributes": True}
