from typing import Literal
from app.modules.payments.providers.base import PaymentProvider
from app.modules.payments.providers.mtn import MtnProvider


def get_provider(name: Literal["mtn"]) -> PaymentProvider:
    if name == "mtn":
        return MtnProvider()
    raise ValueError(f"Provider inconnu: {name}")
