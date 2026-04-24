import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate


async def list_tickets(db: AsyncSession) -> list[Ticket]:
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    return list(result.scalars().all())


async def get_ticket(ticket_id: uuid.UUID, db: AsyncSession) -> Ticket:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    return ticket


async def create_ticket(payload: TicketCreate, db: AsyncSession) -> Ticket:
    ticket = Ticket(**payload.model_dump())
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def update_ticket(ticket_id: uuid.UUID, payload: TicketUpdate, db: AsyncSession) -> Ticket:
    ticket = await get_ticket(ticket_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    await db.commit()
    await db.refresh(ticket)
    return ticket
