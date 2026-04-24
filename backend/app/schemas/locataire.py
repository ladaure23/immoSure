from uuid import UUID
from decimal import Decimal
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
    wallet_solde: Decimal
    score_fiabilite: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletInfo(BaseModel):
    locataire_id: UUID
    solde: Decimal
    loyer_mensuel: Decimal | None
    taux_provisionnement: int  # 0-100
    historique: list["DepotWalletRead"]

    model_config = {"from_attributes": True}


# Import différé pour éviter la circularité
from app.schemas.depot_wallet import DepotWalletRead  # noqa: E402
WalletInfo.model_rebuild()
