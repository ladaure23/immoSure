import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Bien(Base):
    __tablename__ = "biens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str | None] = mapped_column(String(200), nullable=True)
    adresse: Mapped[str] = mapped_column(String(500), nullable=False)
    type_bien: Mapped[str] = mapped_column(String(50), nullable=False)  # immeuble/villa/maison/studio/magasin/autre
    proprietaire_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proprietaires.id"), nullable=False)
    agence_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agences.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    proprietaire: Mapped["Proprietaire"] = relationship(back_populates="biens")
    agence: Mapped["Agence | None"] = relationship(back_populates="biens")
    locations: Mapped[list["Location"]] = relationship(back_populates="bien")
