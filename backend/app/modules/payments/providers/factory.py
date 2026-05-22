from app.modules.payments.providers.base import PaymentProvider
from app.modules.payments.providers.fedapay import FedapayProvider

_instance: FedapayProvider | None = None


def get_provider() -> PaymentProvider:
    global _instance
    if _instance is None:
        _instance = FedapayProvider()
    return _instance
