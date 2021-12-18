"""add repo options

Revision ID: 4cbbca77f13a
Revises: be92d3ad0807
Create Date: 2021-12-18 19:33:22.827402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cbbca77f13a'
down_revision = 'be92d3ad0807'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'option',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.String(255), nullable=False),
        sa.Column('repo_id', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('option')
