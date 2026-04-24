import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contrats.id"), nullable=False)
    type_ticket: Mapped[str] = mapped_column(String(50), nullable=False)  # maintenance/conflit/difficulte_paiement
    description: Mapped[str] = mapped_column(Text, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouvert")  # ouvert/en_cours/ferme
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    contrat: Mapped["Contrat"] = relationship(back_populates="tickets")
