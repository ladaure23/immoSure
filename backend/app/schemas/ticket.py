from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


TypeTicket = Literal["maintenance", "conflit", "difficulte_paiement"]


class TicketBase(BaseModel):
    contrat_id: UUID
    type_ticket: TypeTicket
    description: str


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    statut: Literal["ouvert", "en_cours", "ferme"]


class TicketRead(TicketBase):
    id: UUID
    statut: Literal["ouvert", "en_cours", "ferme"]
    created_at: datetime

    model_config = {"from_attributes": True}
