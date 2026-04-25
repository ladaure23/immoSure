"""
Seed script — crée une agence, un compte utilisateur, des propriétaires,
des biens, des locataires et des contrats de test.
Usage: python seed.py
"""
import asyncio
import uuid
from decimal import Decimal
from datetime import date
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://immosure:immosure_dev_2026@localhost:5432/immosure"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def seed():
    from app.models import Agence, Proprietaire, Locataire, Bien, Contrat, User, Ticket
    from app.database import Base

    async with AsyncSessionLocal() as db:

        # ── Agence ──────────────────────────────────────────────────────────
        agence = Agence(
            id=uuid.uuid4(),
            raison_sociale="ImmoSure Cotonou",
            registre_commerce="RC-BEN-2024-001",
            commission_taux=Decimal("8.00"),
            contact_responsable="Adjonou Kévin",
            telephone="+229 97 11 22 33",
            email="contact@immosure.bj",
            statut_partenariat="actif",
        )
        db.add(agence)
        await db.flush()

        # ── User (compte agence) ─────────────────────────────────────────────
        user = User(
            email="admin@immosure.bj",
            password_hash=_hash_pw("immo2026!"),
            role="agence",
            agence_id=agence.id,
        )
        db.add(user)

        # ── Propriétaires ────────────────────────────────────────────────────
        proprio1 = Proprietaire(
            id=uuid.uuid4(),
            nom="Adjovi",
            prenom="Barnabé",
            telephone="+229 96 00 11 22",
            compte_mobile_money="22996001122",
            operateur_mobile="MTN",
            localisation="Cotonou, Cadjehoun",
            agence_id=agence.id,
        )
        proprio2 = Proprietaire(
            id=uuid.uuid4(),
            nom="Dossou",
            prenom="Euphrasie",
            telephone="+229 97 33 44 55",
            compte_mobile_money="22997334455",
            operateur_mobile="MOOV",
            localisation="Cotonou, Fidjrossè",
            agence_id=agence.id,
        )
        proprio3 = Proprietaire(
            id=uuid.uuid4(),
            nom="Hounsa",
            prenom="Gildas",
            telephone="+229 95 66 77 88",
            compte_mobile_money="22995667788",
            operateur_mobile="WAVE",
            localisation="Porto-Novo, Stade",
            agence_id=agence.id,
        )
        db.add_all([proprio1, proprio2, proprio3])
        await db.flush()

        # ── Biens ────────────────────────────────────────────────────────────
        bien1 = Bien(
            id=uuid.uuid4(),
            adresse="Lot 45 Rue des Cocotiers, Cadjehoun, Cotonou",
            type_bien="appartement",
            proprietaire_id=proprio1.id,
            agence_id=agence.id,
            loyer_mensuel=Decimal("120000"),
            statut="loue",
        )
        bien2 = Bien(
            id=uuid.uuid4(),
            adresse="Villa 12 Résidence Bel Air, Fidjrossè, Cotonou",
            type_bien="villa",
            proprietaire_id=proprio1.id,
            agence_id=agence.id,
            loyer_mensuel=Decimal("250000"),
            statut="loue",
        )
        bien3 = Bien(
            id=uuid.uuid4(),
            adresse="Studio B4 Immeuble Soleil, Haie Vive, Cotonou",
            type_bien="studio",
            proprietaire_id=proprio2.id,
            agence_id=agence.id,
            loyer_mensuel=Decimal("75000"),
            statut="loue",
        )
        bien4 = Bien(
            id=uuid.uuid4(),
            adresse="Magasin 3 Marché Dantokpa, Zone Commerciale",
            type_bien="magasin",
            proprietaire_id=proprio2.id,
            agence_id=agence.id,
            loyer_mensuel=Decimal("180000"),
            statut="loue",
        )
        bien5 = Bien(
            id=uuid.uuid4(),
            adresse="Appartement 2A Résidence du Lac, Porto-Novo",
            type_bien="appartement",
            proprietaire_id=proprio3.id,
            agence_id=agence.id,
            loyer_mensuel=Decimal("95000"),
            statut="disponible",
        )
        db.add_all([bien1, bien2, bien3, bien4, bien5])
        await db.flush()

        # ── Locataires ───────────────────────────────────────────────────────
        loc1 = Locataire(
            id=uuid.uuid4(),
            nom="Mensah",
            prenom="Kofi",
            telephone="+229 97 10 20 30",
            wallet_solde=Decimal("120000"),  # wallet plein → vert
            score_fiabilite=92,
        )
        loc2 = Locataire(
            id=uuid.uuid4(),
            nom="Amoussou",
            prenom="Félicité",
            telephone="+229 96 40 50 60",
            wallet_solde=Decimal("175000"),  # wallet plein → vert
            score_fiabilite=85,
        )
        loc3 = Locataire(
            id=uuid.uuid4(),
            nom="Gbaguidi",
            prenom="Romuald",
            telephone="+229 95 70 80 90",
            wallet_solde=Decimal("40000"),   # wallet partiel → orange (53%)
            score_fiabilite=61,
        )
        loc4 = Locataire(
            id=uuid.uuid4(),
            nom="Ahlonsou",
            prenom="Diane",
            telephone="+229 97 01 23 45",
            wallet_solde=Decimal("15000"),   # wallet vide → rouge (8%)
            score_fiabilite=38,
        )
        db.add_all([loc1, loc2, loc3, loc4])
        await db.flush()

        # ── Contrats ─────────────────────────────────────────────────────────
        contrat1 = Contrat(
            bien_id=bien1.id,
            locataire_id=loc1.id,
            date_debut=date(2025, 1, 1),
            loyer_montant=Decimal("120000"),
            jour_echeance=5,
            statut="actif",
        )
        contrat2 = Contrat(
            bien_id=bien2.id,
            locataire_id=loc2.id,
            date_debut=date(2025, 3, 1),
            loyer_montant=Decimal("250000"),
            jour_echeance=1,
            statut="actif",
        )
        contrat3 = Contrat(
            bien_id=bien3.id,
            locataire_id=loc3.id,
            date_debut=date(2025, 6, 1),
            loyer_montant=Decimal("75000"),
            jour_echeance=10,
            statut="actif",
        )
        contrat4 = Contrat(
            bien_id=bien4.id,
            locataire_id=loc4.id,
            date_debut=date(2025, 9, 1),
            loyer_montant=Decimal("180000"),
            jour_echeance=3,
            statut="actif",
        )
        db.add_all([contrat1, contrat2, contrat3, contrat4])
        await db.flush()

        # ── Tickets ──────────────────────────────────────────────────────────
        ticket1 = Ticket(
            contrat_id=contrat3.id,
            type_ticket="maintenance",
            description="Fuite d'eau au plafond de la salle de bain depuis 3 jours.",
            statut="ouvert",
        )
        ticket2 = Ticket(
            contrat_id=contrat4.id,
            type_ticket="difficulte_paiement",
            description="Locataire signale une difficulté de paiement ce mois — en attente de virement Mobile Money.",
            statut="en_cours",
        )
        db.add_all([ticket1, ticket2])

        await db.commit()
        print("✅ Seed terminé !")
        print(f"   Agence   : {agence.raison_sociale} ({agence.id})")
        print(f"   Login    : admin@immosure.bj / immo2026!")
        print(f"   Biens    : 5 (4 loués, 1 disponible)")
        print(f"   Contrats : 4 actifs")
        print(f"   Tickets  : 2")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/root/projects/immoSure/backend")
    asyncio.run(seed())
