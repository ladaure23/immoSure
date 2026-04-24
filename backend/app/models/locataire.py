import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Locataire(Base):
    __tablename__ = "locataires"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    telephone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(100))
    whatsapp_id: Mapped[str | None] = mapped_column(String(100))
    wallet_solde: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    score_fiabilite: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    contrats: Mapped[list["Contrat"]] = relationship(back_populates="locataire")
    depots: Mapped[list["DepotWallet"]] = relationship(back_populates="locataire")
