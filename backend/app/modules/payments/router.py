import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.schemas.transaction import TransactionRead, DashboardStats, PaiementResultat, BatchPaiementResultat
from app.schemas.depot_wallet import DepotInitierMtn, DepotResponse
from app.modules.payments import service
from app.modules.payments import split_service

router = APIRouter(tags=["payments"])

# --- Transactions (protégées) ---

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


# --- Wallet dépôts (protégés) ---

wallet_router = APIRouter(
    prefix="/api/wallet",
    dependencies=[Depends(get_current_user)],
)


@wallet_router.post("/depot/mtn", response_model=DepotResponse, status_code=201)
async def initier_depot_mtn(payload: DepotInitierMtn, db: AsyncSession = Depends(get_db)):
    return await service.initier_depot_mtn(payload, db)


# --- Webhooks (sans JWT — appelés par MTN) ---

webhooks_router = APIRouter(prefix="/api/wallet")


@webhooks_router.post("/webhook/mtn")
async def webhook_mtn(request: Request, db: AsyncSession = Depends(get_db)):
    raw = await request.body()
    return await service.handle_webhook_mtn(raw, db)


# --- Split / paiements automatiques (admin uniquement) ---

split_router = APIRouter(prefix="/api", tags=["split"])


@split_router.post(
    "/contrats/{contrat_id}/payer",
    response_model=PaiementResultat,
    dependencies=[Depends(require_admin)],
)
async def payer_contrat(contrat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await split_service.executer_paiement_contrat(contrat_id, db)


@split_router.post(
    "/paiements/executer-jour",
    response_model=BatchPaiementResultat,
    dependencies=[Depends(require_admin)],
)
async def executer_paiements_du_jour(db: AsyncSession = Depends(get_db)):
    return await split_service.executer_paiements_du_jour(db)


# Inclure tous les sous-routers dans router principal
router.include_router(transactions_router)
router.include_router(wallet_router)
router.include_router(webhooks_router)
router.include_router(split_router)
