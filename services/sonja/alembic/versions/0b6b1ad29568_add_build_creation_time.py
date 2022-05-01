"""add build creation time

Revision ID: 0b6b1ad29568
Revises: e7a691a4442c
Create Date: 2022-04-25 13:14:47.459799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b6b1ad29568'
down_revision = 'e7a691a4442c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'build',
        sa.Column('created', sa.DateTime, index=True)
    )


def downgrade():
    op.drop_column('build', 'created')
