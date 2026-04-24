import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Proprietaire(Base):
    __tablename__ = "proprietaires"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    telephone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    compte_mobile_money: Mapped[str | None] = mapped_column(String(20))
    operateur_mobile: Mapped[str | None] = mapped_column(String(20))  # MTN / MOOV / WAVE
    whatsapp_id: Mapped[str | None] = mapped_column(String(100))
    telegram_chat_id: Mapped[str | None] = mapped_column(String(100))
    localisation: Mapped[str | None] = mapped_column(String(300))
    agence_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agences.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    agence: Mapped["Agence | None"] = relationship(back_populates="proprietaires")
    biens: Mapped[list["Bien"]] = relationship(back_populates="proprietaire")
