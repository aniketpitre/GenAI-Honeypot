"""initial schema

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "tokens",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("decoy_url", sa.Text, nullable=True),
        sa.Column("external_key", sa.String(200), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("hit_id", sa.String(64), nullable=True, unique=True),
        sa.Column("token_id", sa.String(32), sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(64), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("country", sa.String(8), nullable=False),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lon", sa.Float, nullable=False),
        sa.Column("user_agent", sa.Text, nullable=False),
        sa.Column("request_path", sa.Text, nullable=False),
        sa.Column("request_headers", sa.JSON, nullable=False),
        sa.Column("notes", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
    )
    op.create_index("ix_alerts_token_id", "alerts", ["token_id"])
    op.create_index("ix_alerts_timestamp", "alerts", ["timestamp"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("tokens")
