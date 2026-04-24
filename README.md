# ImmoSure — Plateforme de Gestion Locative

Gestion locative automatisée pour le Bénin (Cotonou).  
Stack : FastAPI + PostgreSQL + React + Tailwind + Bot Telegram + FedaPay + KKiaPay + Claude API

## Démarrage rapide

```bash
cp backend/.env.example backend/.env
# Éditez backend/.env avec vos clés API

make install
make migrate
make dev
```

## Déploiement VPS

```bash
sudo REPO_URL=https://github.com/yourorg/immosure.git \
     DB_PASSWORD=motdepasse_securise \
     bash setup-vps.sh
```

## Commandes

| Commande | Description |
|---|---|
| `make install` | Installe dépendances Python + Node |
| `make dev` | Lance backend + frontend en développement |
| `make build` | Compile le frontend React |
| `make migrate` | Applique les migrations Alembic |
| `make deploy` | Build + redémarre PM2 |
| `make logs` | Affiche les logs PM2 |

## Architecture

```
backend/app/
├── main.py              # Entry point FastAPI
├── config.py            # Settings (pydantic-settings)
├── database.py          # SQLAlchemy async engine
├── models/              # ORM models
├── schemas/             # Pydantic schemas
└── modules/
    ├── auth/            # JWT
    ├── agences/
    ├── proprietaires/
    ├── locataires/
    ├── biens/
    ├── contrats/
    ├── payments/        # FedaPay + KKiaPay + split automatique
    ├── notifications/   # Telegram, WhatsApp, SMS
    ├── pdf/             # Reçus tripartites WeasyPrint
    ├── bot/             # Bot Telegram
    ├── scheduler/       # APScheduler J-7/J-5/J-3/J-1
    └── tickets/
```

## Répartition des paiements

| Bénéficiaire | Taux |
|---|---|
| Propriétaire | 89% du loyer |
| Agence | 8% |
| Plateforme | 2% |
| Fonds maintenance | 1% |
