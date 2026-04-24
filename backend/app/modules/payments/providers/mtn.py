import uuid
import base64
from decimal import Decimal
import httpx
from fastapi import HTTPException, status
from app.config import settings
from app.modules.payments.providers.base import PaymentProvider, InitiationResult


class MtnProvider(PaymentProvider):
    async def _get_token(self, client: httpx.AsyncClient) -> str:
        credentials = base64.b64encode(
            f"{settings.mtn_api_user}:{settings.mtn_api_key}".encode()
        ).decode()
        resp = await client.post(
            f"{settings.mtn_base_url}/collection/token/",
            headers={
                "Authorization": f"Basic {credentials}",
                "Ocp-Apim-Subscription-Key": settings.mtn_subscription_key,
            },
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"MTN token error: {resp.text}",
            )
        return resp.json()["access_token"]

    async def initier_paiement(
        self,
        montant: Decimal,
        telephone: str,
        depot_id: str,
        description: str = "Dépôt wallet ImmoSure",
    ) -> InitiationResult:
        reference = str(uuid.uuid4())
        async with httpx.AsyncClient(timeout=15.0) as client:
            token = await self._get_token(client)
            resp = await client.post(
                f"{settings.mtn_base_url}/collection/v1_0/requesttopay",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Reference-Id": reference,
                    "X-Target-Environment": settings.mtn_env,
                    "Ocp-Apim-Subscription-Key": settings.mtn_subscription_key,
                    "X-Callback-Url": f"{settings.app_url}/api/wallet/webhook/mtn",
                    "Content-Type": "application/json",
                },
                json={
                    "amount": str(int(montant)),
                    "currency": "XOF",
                    "externalId": depot_id,
                    "payer": {
                        "partyIdType": "MSISDN",
                        "partyId": telephone,
                    },
                    "payerMessage": description,
                    "payeeNote": description,
                },
            )
            if resp.status_code != 202:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"MTN MoMo error: {resp.text}",
                )
            # MTN envoie un USSD push au téléphone — pas d'URL de redirection
            return InitiationResult(payment_url="", reference=reference)

    def verifier_signature_webhook(self, payload_bytes: bytes, signature: str | None) -> bool:
        # MTN ne signe pas ses callbacks via HMAC
        # La vérification se fait en re-fetchant le statut via GET /requesttopay/{reference}
        return True
