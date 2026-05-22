"""Add locations table — Location layer between Bien and Contrat

Revision ID: 002
Revises: 001
"""
from typing import Union
import uuid
import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Créer la table locations
    op.create_table(
        "locations",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bien_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("biens.id"), nullable=False),
        sa.Column("nom", sa.String(200), nullable=False),
        sa.Column("type_location", sa.String(50), nullable=False),
        sa.Column("surface_m2", sa.Numeric(8, 2), nullable=True),
        sa.Column("loyer_mensuel", sa.Numeric(12, 2), nullable=False),
        sa.Column("statut", sa.String(20), nullable=False, server_default="disponible"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_locations_bien_id", "locations", ["bien_id"])

    # 2. Ajouter location_id (nullable) et duree_type à contrats
    op.add_column("contrats", sa.Column("location_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("contrats", sa.Column("duree_type", sa.String(20), nullable=False, server_default="indefini"))

    # 3. Migration des données existantes
    connection = op.get_bind()

    biens = connection.execute(
        sa.text("SELECT id, type_bien, loyer_mensuel, statut FROM biens")
    ).fetchall()

    for bien in biens:
        location_id = str(uuid.uuid4())
        connection.execute(
            sa.text("""
                INSERT INTO locations (id, bien_id, nom, type_location, loyer_mensuel, statut, created_at)
                VALUES (:id, :bien_id, 'Principal', :type_location, :loyer_mensuel, :statut, NOW())
            """),
            {
                "id": location_id,
                "bien_id": str(bien.id),
                "type_location": bien.type_bien,
                "loyer_mensuel": bien.loyer_mensuel,
                "statut": bien.statut,
            },
        )
        connection.execute(
            sa.text("UPDATE contrats SET location_id = :loc_id WHERE bien_id = :bien_id"),
            {"loc_id": location_id, "bien_id": str(bien.id)},
        )

    # 4. Rendre location_id NOT NULL
    op.alter_column("contrats", "location_id", nullable=False)

    # 5. Ajouter FK constraint sur location_id
    op.create_foreign_key("fk_contrats_location_id", "contrats", "locations", ["location_id"], ["id"])

    # 6. Supprimer l'ancienne FK bien_id et la colonne
    op.drop_constraint("contrats_bien_id_fkey", "contrats", type_="foreignkey")
    op.drop_column("contrats", "bien_id")

    # 7. Supprimer loyer_mensuel et statut de biens
    op.drop_column("biens", "loyer_mensuel")
    op.drop_column("biens", "statut")


def downgrade() -> None:
    # Réajouter loyer_mensuel et statut à biens
    op.add_column("biens", sa.Column("loyer_mensuel", sa.Numeric(12, 2), nullable=True))
    op.add_column("biens", sa.Column("statut", sa.String(20), nullable=True))

    # Réajouter bien_id à contrats
    op.add_column("contrats", sa.Column("bien_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))

    # Restaurer les données depuis locations
    connection = op.get_bind()
    rows = connection.execute(
        sa.text("""
            SELECT c.id as contrat_id, l.bien_id, l.loyer_mensuel, l.statut
            FROM contrats c JOIN locations l ON c.location_id = l.id
        """)
    ).fetchall()
    for row in rows:
        connection.execute(
            sa.text("UPDATE contrats SET bien_id = :bien_id WHERE id = :contrat_id"),
            {"bien_id": str(row.bien_id), "contrat_id": str(row.contrat_id)},
        )
        connection.execute(
            sa.text("UPDATE biens SET loyer_mensuel = :loyer, statut = :statut WHERE id = :bien_id"),
            {"loyer": row.loyer_mensuel, "statut": row.statut, "bien_id": str(row.bien_id)},
        )

    op.alter_column("contrats", "bien_id", nullable=False)
    op.create_foreign_key("contrats_bien_id_fkey", "contrats", "biens", ["bien_id"], ["id"])
    op.drop_constraint("fk_contrats_location_id", "contrats", type_="foreignkey")
    op.drop_column("contrats", "location_id")
    op.drop_column("contrats", "duree_type")
    op.drop_index("ix_locations_bien_id", table_name="locations")
    op.drop_table("locations")
