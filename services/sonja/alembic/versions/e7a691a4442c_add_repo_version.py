"""add repo version

Revision ID: e7a691a4442c
Revises: 12c2eb94c088
Create Date: 2022-03-16 12:37:42.033144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7a691a4442c'
down_revision = '12c2eb94c088'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'repo',
        sa.Column('version', sa.String(255))
    )


def downgrade():
    op.drop_column('repo', 'version')
