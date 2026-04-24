import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class DepotWallet(Base):
    __tablename__ = "depots_wallet"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    locataire_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("locataires.id"), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference_provider: Mapped[str | None] = mapped_column(String(200))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # mtn / ...
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="en_attente")  # en_attente/complete/echoue
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    locataire: Mapped["Locataire"] = relationship(back_populates="depots")
