import uuid
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import String, Numeric, Integer, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Contrat(Base):
    __tablename__ = "contrats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bien_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("biens.id"), nullable=False)
    locataire_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("locataires.id"), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    loyer_montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    jour_echeance: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="actif")  # actif/resilie/expire
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    bien: Mapped["Bien"] = relationship(back_populates="contrats")
    locataire: Mapped["Locataire"] = relationship(back_populates="contrats")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="contrat")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="contrat")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="contrat")
