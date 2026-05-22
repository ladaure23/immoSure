import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bien_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("biens.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_location: Mapped[str] = mapped_column(String(50), nullable=False)  # appartement/studio/chambre/magasin/bureau/autre
    surface_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    loyer_mensuel: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="disponible")  # disponible/loue
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    bien: Mapped["Bien"] = relationship(back_populates="locations")
    contrats: Mapped[list["Contrat"]] = relationship(back_populates="location")
