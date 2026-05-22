"""
Calcul du split FedaPay Marketplace.

Règles :
  - Propriétaire : 90 % calculés sur le montant BRUT (garanti, pas impacté par les frais)
  - Agence + Plateforme : 10 % calculés sur le montant BRUT
    └ Les frais FedaPay (1.8 % MTN / 4 % MOOV) sont déduits de ces 10 %
    └ Agence reçoit 80 % du net agence+plateforme (soit ~8 % du brut - sa part des frais)
    └ Plateforme garde 20 % du net agence+plateforme (soit ~2 % du brut - sa part des frais)
      → reste sur le compte principal FedaPay, pas de sous-compte

Taux FedaPay par moyen de paiement (Bénin) :
  MTN Mobile Money : 1.8 %
  MOOV Money       : 4.0 %
"""
from decimal import Decimal, ROUND_DOWN
from typing import Literal
from app.modules.payments.providers.base import SplitEntry

_TAUX_PROPRIO = Decimal("90")
_TAUX_AGENCE_PLATEFORME = Decimal("10")
_TAUX_AGENCE_SUR_NET = Decimal("80")   # 8/10 du bloc agence+plateforme
_CENT = Decimal("100")
_CENTIME = Decimal("0.01")

TAUX_FEDAPAY: dict[str, Decimal] = {
    "mtn":  Decimal("1.8"),
    "moov": Decimal("4.0"),
}


def calculer_split(
    montant_brut: Decimal,
    operateur: Literal["mtn", "moov"] = "mtn",
    has_agence: bool = True,
    ref_proprietaire: str | None = None,
    ref_agence: str | None = None,
    ref_plateforme: str | None = None,
) -> dict:
    """
    Retourne les montants et la liste des SplitEntry FedaPay.

    Le propriétaire reçoit 90 % du brut via son sous-compte.
    L'agence reçoit sa part du net via son sous-compte.
    La plateforme garde le reste sur le compte principal (pas de SplitEntry).
    """
    taux_fedapay = TAUX_FEDAPAY.get(operateur, Decimal("1.8"))

    # Part propriétaire — sur le brut, arrondie au centime inférieur
    part_proprio = (montant_brut * _TAUX_PROPRIO / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN)

    # Bloc agence+plateforme — 10 % du brut
    bloc_ap = montant_brut - part_proprio

    # Frais FedaPay prélevés sur le montant total — répercutés uniquement sur le bloc 10 %
    frais = (montant_brut * taux_fedapay / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN)
    net_ap = bloc_ap - frais
    if net_ap < Decimal("0"):
        net_ap = Decimal("0")

    if has_agence and net_ap > 0:
        part_agence = (net_ap * _TAUX_AGENCE_SUR_NET / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN)
    else:
        part_agence = Decimal("0")

    part_plateforme = net_ap - part_agence  # reste sur compte principal

    # Construction des SplitEntry (uniquement si sous-compte connu)
    splits: list[SplitEntry] = []
    if ref_proprietaire and int(part_proprio) > 0:
        splits.append(SplitEntry(reference=ref_proprietaire, amount=int(part_proprio)))
    if ref_agence and has_agence and int(part_agence) > 0:
        splits.append(SplitEntry(reference=ref_agence, amount=int(part_agence)))
    if ref_plateforme and int(part_plateforme) > 0:
        splits.append(SplitEntry(reference=ref_plateforme, amount=int(part_plateforme)))

    return {
        "montant_brut": montant_brut,
        "frais_fedapay": frais,
        "montant_net": montant_brut - frais,
        "part_proprietaire": part_proprio,
        "part_agence": part_agence,
        "part_plateforme": part_plateforme,
        "splits": splits,
    }
