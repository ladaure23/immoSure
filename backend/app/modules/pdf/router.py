import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.modules.pdf.generator import generate_quittance

router = APIRouter(prefix="/api/transactions", tags=["pdf"])


@router.get("/{transaction_id}/quittance")
async def telecharger_quittance(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    pdf = await generate_quittance(transaction_id, db)
    if pdf is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction introuvable ou statut non complété",
        )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=quittance-{transaction_id}.pdf"
        },
    )
