import uuid
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contrats.id"), nullable=False)
    montant_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    montant_net: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    frais_fedapay: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    part_proprietaire: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    part_agence: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    part_plateforme: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="en_attente")
    fedapay_transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reference_paiement: Mapped[str | None] = mapped_column(String(200), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mois_concerne: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    contrat: Mapped["Contrat"] = relationship(back_populates="transactions")
