import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.transaction import TransactionRead, DashboardStats
from app.schemas.paiement_loyer import PaiementLoyerRead, InitierPaiementPayload, InitierPaiementResponse
from app.schemas.proprietaire import InvitationFedapayResult
from app.modules.payments import service

router = APIRouter(tags=["payments"])

# ── Transactions ──────────────────────────────────────────────────────────────

transactions_router = APIRouter(
    prefix="/api/transactions",
    dependencies=[Depends(get_current_user)],
)


@transactions_router.get("", response_model=list[TransactionRead])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    return await service.list_transactions(db)


@transactions_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    return await service.get_dashboard_stats(db)


@transactions_router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_transaction(transaction_id, db)


# ── Paiements loyer ───────────────────────────────────────────────────────────

paiements_router = APIRouter(
    prefix="/api/paiements",
    dependencies=[Depends(get_current_user)],
)


@paiements_router.post("/initier", response_model=InitierPaiementResponse, status_code=201)
async def initier_paiement(payload: InitierPaiementPayload, db: AsyncSession = Depends(get_db)):
    return await service.initier_paiement_loyer(payload, db)


@paiements_router.get("/loyer/{contrat_id}", response_model=list[PaiementLoyerRead])
async def get_paiements_loyer(contrat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_paiements_loyer(contrat_id, db)


# ── Webhooks FedaPay (sans JWT) ───────────────────────────────────────────────

webhooks_router = APIRouter(prefix="/api/webhooks")


@webhooks_router.post("/fedapay")
async def webhook_fedapay(request: Request, db: AsyncSession = Depends(get_db)):
    raw = await request.body()
    signature = request.headers.get("X-FEDAPAY-SIGNATURE")
    return await service.handle_webhook_fedapay(raw, signature, db)


# ── Invitations FedaPay ───────────────────────────────────────────────────────

invitations_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)],
)


@invitations_router.post("/proprietaires/{proprietaire_id}/inviter-fedapay", response_model=InvitationFedapayResult)
async def inviter_proprietaire(proprietaire_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.inviter_proprietaire_fedapay(proprietaire_id, db)


@invitations_router.post("/agences/{agence_id}/inviter-fedapay", response_model=InvitationFedapayResult)
async def inviter_agence(agence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.inviter_agence_fedapay(agence_id, db)


# ── Assemblage ────────────────────────────────────────────────────────────────

router.include_router(transactions_router)
router.include_router(paiements_router)
router.include_router(webhooks_router)
router.include_router(invitations_router)
