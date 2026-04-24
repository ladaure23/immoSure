"""
Service de split automatique des paiements.

Règles de répartition :
  - Propriétaire : 89 %
  - Agence       :  8 % (si bien rattaché à une agence, sinon reversé au propriétaire)
  - Plateforme   :  2 %
  - Maintenance  :  1 %

Le split est calculé par soustraction successive (ROUND_DOWN sur les 3 premières parts,
remainder pour la 4e) pour garantir que la somme == montant_total sans arrondi parasite.
"""
import uuid
from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_DOWN
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from app.models.contrat import Contrat
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.models.transaction import Transaction
from app.schemas.transaction import PaiementResultat, BatchPaiementResultat

_TAUX_PROPRIETAIRE = Decimal("89")
_TAUX_AGENCE = Decimal("8")
_TAUX_PLATEFORME = Decimal("2")
_CENT = Decimal("100")
_CENTIME = Decimal("0.01")


def calculer_split(montant: Decimal, has_agence: bool = True) -> dict[str, Decimal]:
    """Retourne les 4 parts de répartition dont la somme == montant."""
    part_plateforme = (montant * _TAUX_PLATEFORME / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN)
    part_agence = (montant * _TAUX_AGENCE / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN) if has_agence else Decimal("0")
    part_proprietaire_base = (montant * _TAUX_PROPRIETAIRE / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN)
    # Sans agence, les 8 % reviennent au propriétaire
    part_proprietaire = part_proprietaire_base if has_agence else part_proprietaire_base + (montant * _TAUX_AGENCE / _CENT).quantize(_CENTIME, rounding=ROUND_DOWN)
    # Maintenance = remainder pour garantir total == montant
    part_maintenance = montant - part_proprietaire - part_agence - part_plateforme
    return {
        "part_proprietaire": part_proprietaire,
        "part_agence": part_agence,
        "part_plateforme": part_plateforme,
        "part_maintenance": part_maintenance,
    }


def _mois_en_cours() -> date:
    today = date.today()
    return today.replace(day=1)


async def _deja_paye_ce_mois(contrat_id: uuid.UUID, mois: date, db: AsyncSession) -> bool:
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.contrat_id == contrat_id,
                Transaction.mois_concerne == mois,
                Transaction.statut == "complete",
            )
        )
    )
    return result.scalar_one_or_none() is not None


async def executer_paiement_contrat(
    contrat_id: uuid.UUID,
    db: AsyncSession,
    mois_concerne: date | None = None,
) -> PaiementResultat:
    """
    Débite le wallet du locataire et crée la Transaction correspondante.
    Idempotent : si déjà payé ce mois, retourne statut 'ignore'.
    """
    result = await db.execute(
        select(Contrat, Bien, Locataire)
        .join(Bien, Contrat.bien_id == Bien.id)
        .join(Locataire, Contrat.locataire_id == Locataire.id)
        .where(Contrat.id == contrat_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrat introuvable")

    contrat, bien, locataire = row

    if contrat.statut != "actif":
        return PaiementResultat(contrat_id=contrat_id, statut="ignore", raison="Contrat non actif")

    mois = mois_concerne or _mois_en_cours()

    if await _deja_paye_ce_mois(contrat_id, mois, db):
        return PaiementResultat(contrat_id=contrat_id, statut="ignore", raison="Déjà payé ce mois")

    montant = contrat.loyer_montant
    split = calculer_split(montant, has_agence=bien.agence_id is not None)

    if locataire.wallet_solde >= montant:
        locataire.wallet_solde -= montant
        locataire.score_fiabilite = min(100, locataire.score_fiabilite + 1)
        transaction_statut = "complete"
    else:
        # Wallet insuffisant — on enregistre l'échec sans débiter
        locataire.score_fiabilite = max(0, locataire.score_fiabilite - 5)
        transaction_statut = "echoue"

    transaction = Transaction(
        contrat_id=contrat_id,
        montant_total=montant,
        mois_concerne=mois,
        statut=transaction_statut,
        **split,
    )
    db.add(transaction)
    await db.commit()

    return PaiementResultat(
        contrat_id=contrat_id,
        statut=transaction_statut,
        montant=montant if transaction_statut == "complete" else None,
        raison="Solde insuffisant" if transaction_statut == "echoue" else None,
    )


async def executer_paiements_du_jour(db: AsyncSession) -> BatchPaiementResultat:
    """
    Déclenche les paiements de tous les contrats actifs dont l'échéance tombe aujourd'hui.
    Appelé par l'APScheduler (étape 6) — peut aussi être déclenché manuellement.
    """
    today = date.today()
    mois = _mois_en_cours()

    result = await db.execute(
        select(Contrat).where(
            and_(Contrat.statut == "actif", Contrat.jour_echeance == today.day)
        )
    )
    contrats = list(result.scalars().all())

    details: list[PaiementResultat] = []
    reussis = echoues = ignores = 0

    for contrat in contrats:
        res = await executer_paiement_contrat(contrat.id, db, mois_concerne=mois)
        details.append(res)
        if res.statut == "complete":
            reussis += 1
        elif res.statut == "echoue":
            echoues += 1
        else:
            ignores += 1

    return BatchPaiementResultat(
        traites=len(contrats),
        reussis=reussis,
        echoues=echoues,
        ignores=ignores,
        details=details,
    )
