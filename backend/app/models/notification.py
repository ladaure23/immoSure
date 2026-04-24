import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destinataire_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    type_destinataire: Mapped[str] = mapped_column(String(20), nullable=False)  # locataire/proprietaire/agence
    canal: Mapped[str] = mapped_column(String(20), nullable=False)  # telegram/whatsapp/sms
    type_notif: Mapped[str] = mapped_column(String(20), nullable=False)  # J-7/J-5/J-3/J-1/confirmation/alerte
    message: Mapped[str] = mapped_column(Text, nullable=False)
    statut_envoi: Mapped[str] = mapped_column(String(20), nullable=False, default="en_attente")  # en_attente/envoye/echoue
    contrat_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("contrats.id"), nullable=True)
    tentatives: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    contrat: Mapped["Contrat | None"] = relationship(back_populates="notifications")
