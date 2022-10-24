"""Timestamp runs

Revision ID: 31d973110d41
Revises: be92d3ad0807
Create Date: 2022-11-14 21:41:34.833114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31d973110d41'
down_revision = 'be92d3ad0807'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("run", sa.Column("updated", sa.DateTime, nullable=False, index=True))


def downgrade():
    op.drop_column("run")
