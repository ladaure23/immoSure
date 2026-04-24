from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class NotificationRead(BaseModel):
    id: UUID
    destinataire_id: UUID
    type_destinataire: Literal["locataire", "proprietaire", "agence"]
    canal: Literal["telegram", "whatsapp", "sms"]
    type_notif: Literal["J-7", "J-5", "J-3", "J-1", "confirmation", "alerte"]
    message: str
    statut_envoi: Literal["en_attente", "envoye", "echoue"]
    contrat_id: UUID | None
    tentatives: int
    created_at: datetime

    model_config = {"from_attributes": True}
