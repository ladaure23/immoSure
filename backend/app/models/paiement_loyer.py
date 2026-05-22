import uuid
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PaiementLoyer(Base):
    __tablename__ = "paiement_loyer"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contrats.id"), nullable=False)
    periode_debut: Mapped[date] = mapped_column(Date, nullable=False)
    periode_fin: Mapped[date] = mapped_column(Date, nullable=False)
    loyer_du: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_paye: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="en_attente")  # en_attente/partiel/complet
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    contrat: Mapped["Contrat"] = relationship(back_populates="paiements_loyer")
