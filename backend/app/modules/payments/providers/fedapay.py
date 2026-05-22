import hmac
import hashlib
import logging
from decimal import Decimal
import httpx
from fastapi import HTTPException, status
from app.config import settings
from app.modules.payments.providers.base import PaymentProvider, InitiationResult, SplitEntry

logger = logging.getLogger(__name__)


class FedapayProvider(PaymentProvider):

    @property
    def _base_url(self) -> str:
        if settings.fedapay_env == "production":
            return "https://api.fedapay.com/v1"
        return "https://sandbox-api.fedapay.com/v1"

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.fedapay_secret_key}",
            "Content-Type": "application/json",
        }

    async def initier_paiement(
        self,
        montant: Decimal,
        telephone: str,
        description: str,
        splits: list[SplitEntry],
        metadata: dict | None = None,
    ) -> InitiationResult:
        payload: dict = {
            "description": description,
            "amount": int(montant),
            "currency": {"iso": "XOF"},
            "customer": {
                "phone_number": {
                    "number": telephone,
                    "country": "BJ",
                }
            },
            "callback_url": f"{settings.app_url}/api/webhooks/fedapay",
        }

        if splits:
            payload["sub_accounts_commissions"] = [
                {"reference": s.reference, "amount": s.amount} for s in splits
            ]

        if metadata:
            payload["custom_metadata"] = metadata

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{self._base_url}/transactions",
                headers=self._headers,
                json=payload,
            )
            # Fallback : si les sous-comptes n'existent pas (sandbox / non encore invités),
            # réessayer sans splits pour ne pas bloquer le paiement.
            if resp.status_code not in (200, 201):
                body = resp.json()
                errors = body.get("errors", {})
                if "sub_accounts_commissions" in errors and splits:
                    logger.warning(
                        "FedaPay: sous-comptes inexistants (%s) — paiement sans split",
                        errors["sub_accounts_commissions"],
                    )
                    payload.pop("sub_accounts_commissions", None)
                    resp = await client.post(
                        f"{self._base_url}/transactions",
                        headers=self._headers,
                        json=payload,
                    )
                if resp.status_code not in (200, 201):
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"FedaPay create transaction error: {resp.text}",
                    )
            data = resp.json().get("v1/transaction", resp.json())
            transaction_id = str(data["id"])
            payment_url = data.get("payment_url", "")

        return InitiationResult(reference=transaction_id, payment_url=payment_url)

    def verifier_signature_webhook(self, payload_bytes: bytes, signature: str | None) -> bool:
        if not signature or not settings.fedapay_webhook_secret:
            return False
        # Format FedaPay : "t=<timestamp>,s=<hmac>"
        # Le message signé est "<timestamp>.<raw_body>"
        try:
            parts = dict(item.split("=", 1) for item in signature.split(","))
            timestamp = parts.get("t", "")
            received_sig = parts.get("s", "")
        except Exception:
            return False
        signed_payload = f"{timestamp}.".encode() + payload_bytes
        expected = hmac.new(
            settings.fedapay_webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, received_sig)

    async def inviter_sous_compte(self, email: str, full_name: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self._base_url}/auth/sub_account_invitations",
                headers=self._headers,
                json={"email": email, "full_name": full_name},
            )
            if resp.status_code not in (200, 201):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"FedaPay invitation error: {resp.text}",
                )
            data = resp.json()
            return data.get("reference", data.get("id", ""))
