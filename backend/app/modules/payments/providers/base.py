from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass, field


@dataclass
class InitiationResult:
    reference: str          # fedapay_transaction_id
    payment_url: str = ""   # URL de paiement à envoyer au locataire


@dataclass
class SplitEntry:
    reference: str   # acc_xxxxxx du sous-compte FedaPay
    amount: int      # montant en XOF (entier)


class PaymentProvider(ABC):
    @abstractmethod
    async def initier_paiement(
        self,
        montant: Decimal,
        telephone: str,
        description: str,
        splits: list[SplitEntry],
        metadata: dict | None = None,
    ) -> InitiationResult: ...

    @abstractmethod
    def verifier_signature_webhook(self, payload_bytes: bytes, signature: str | None) -> bool: ...

    @abstractmethod
    async def inviter_sous_compte(self, email: str, full_name: str) -> str:
        """Envoie une invitation FedaPay et retourne la référence du sous-compte."""
        ...
