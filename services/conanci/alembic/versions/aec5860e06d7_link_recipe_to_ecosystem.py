"""Link recipe to ecosystem

Revision ID: aec5860e06d7
Revises: be92d3ad0807
Create Date: 2021-05-17 15:30:35.050105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aec5860e06d7'
down_revision = 'be92d3ad0807'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'recipe',
        sa.Column('ecosystem_id', sa.Integer(), sa.ForeignKey('ecosystem.id'))
    )


def downgrade():
    op.drop_column('recipe', 'ecosystem_id')
