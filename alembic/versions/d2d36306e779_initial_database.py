"""Initial Database.

Revision ID: d2d36306e779
Revises:
Create Date: 2023-02-10 13:40:56.504935

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "d2d36306e779"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create frontdoor_ranges and frontdoor_ips tables."""
    op.create_table(
        "frontdoor_ranges",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ranges", sa.ARRAY(sa.String)),
        sa.Column("last_updated", sa.DateTime),
    )
    op.create_table(
        "frontdoor_ips",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain", sa.String),
        sa.Column("ips", sa.ARRAY(sa.String)),
        sa.Column("last_updated", sa.DateTime),
    )


def downgrade() -> None:
    """Drop frontdoor_ranges and frontdoor_ips tables."""
    op.drop_table("frontdoor_ranges")
    op.drop_table("frontdoor_ips")
