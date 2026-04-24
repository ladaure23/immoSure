import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketRead
from app.modules.tickets import service

router = APIRouter(prefix="/api/tickets", tags=["tickets"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[TicketRead])
async def list_tickets(db: AsyncSession = Depends(get_db)):
    return await service.list_tickets(db)


@router.post("", response_model=TicketRead, status_code=201)
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_ticket(payload, db)


@router.put("/{ticket_id}", response_model=TicketRead)
async def update_ticket(ticket_id: uuid.UUID, payload: TicketUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_ticket(ticket_id, payload, db)
