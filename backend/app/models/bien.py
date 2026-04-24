import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Bien(Base):
    __tablename__ = "biens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adresse: Mapped[str] = mapped_column(String(500), nullable=False)
    type_bien: Mapped[str] = mapped_column(String(50), nullable=False)  # appartement/villa/studio/magasin
    proprietaire_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proprietaires.id"), nullable=False)
    agence_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agences.id"), nullable=True)
    loyer_mensuel: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="disponible")  # disponible/loue
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    proprietaire: Mapped["Proprietaire"] = relationship(back_populates="biens")
    agence: Mapped["Agence | None"] = relationship(back_populates="biens")
    contrats: Mapped[list["Contrat"]] = relationship(back_populates="bien")
