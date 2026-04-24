from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class InitiationResult:
    reference: str      # identifiant côté provider (pour matcher le webhook)
    payment_url: str = ""  # vide pour les providers USSD-push (ex: MTN)


class PaymentProvider(ABC):
    @abstractmethod
    async def initier_paiement(
        self,
        montant: Decimal,
        telephone: str,
        depot_id: str,
        description: str = "Dépôt wallet ImmoSure",
    ) -> InitiationResult: ...

    @abstractmethod
    def verifier_signature_webhook(self, payload_bytes: bytes, signature: str | None) -> bool: ...

    async def verifier_transaction(self, reference: str) -> bool:
        """Re-vérifie le statut côté provider avant de créditer. Override pour les providers sans HMAC."""
        return True
