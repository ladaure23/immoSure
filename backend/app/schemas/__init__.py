from app.schemas.agence import AgenceCreate, AgenceUpdate, AgenceRead
from app.schemas.proprietaire import ProprietaireCreate, ProprietaireUpdate, ProprietaireRead
from app.schemas.locataire import LocataireCreate, LocataireUpdate, LocataireRead, WalletInfo
from app.schemas.bien import BienCreate, BienUpdate, BienRead
from app.schemas.contrat import ContratCreate, ContratUpdate, ContratRead, ContratRisque
from app.schemas.transaction import TransactionRead, DashboardStats
from app.schemas.depot_wallet import DepotInitierFedapay, DepotInitierKkiapay, DepotWalletRead, DepotResponse
from app.schemas.notification import NotificationRead
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketRead
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead

__all__ = [
    "AgenceCreate", "AgenceUpdate", "AgenceRead",
    "ProprietaireCreate", "ProprietaireUpdate", "ProprietaireRead",
    "LocataireCreate", "LocataireUpdate", "LocataireRead", "WalletInfo",
    "BienCreate", "BienUpdate", "BienRead",
    "ContratCreate", "ContratUpdate", "ContratRead", "ContratRisque",
    "TransactionRead", "DashboardStats",
    "DepotInitierFedapay", "DepotInitierKkiapay", "DepotWalletRead", "DepotResponse",
    "NotificationRead",
    "TicketCreate", "TicketUpdate", "TicketRead",
    "LoginRequest", "RegisterRequest", "TokenResponse", "UserRead",
]
