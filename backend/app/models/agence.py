import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Agence(Base):
    __tablename__ = "agences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raison_sociale: Mapped[str] = mapped_column(String(200), nullable=False)
    registre_commerce: Mapped[str | None] = mapped_column(String(100), unique=True)
    commission_taux: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("8.00"))
    contact_responsable: Mapped[str | None] = mapped_column(String(200))
    telephone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    statut_partenariat: Mapped[str] = mapped_column(String(50), nullable=False, default="actif")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    proprietaires: Mapped[list["Proprietaire"]] = relationship(back_populates="agence")
    biens: Mapped[list["Bien"]] = relationship(back_populates="agence")
    users: Mapped[list["User"]] = relationship(back_populates="agence")
