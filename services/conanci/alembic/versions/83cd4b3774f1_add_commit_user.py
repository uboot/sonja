"""Add commit user

Revision ID: 83cd4b3774f1
Revises: be92d3ad0807
Create Date: 2021-04-17 12:10:08.191143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83cd4b3774f1'
down_revision = 'be92d3ad0807'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('commit', sa.Column('user_name', sa.String(255)))
    op.add_column('commit', sa.Column('user_email', sa.String(255)))


def downgrade():
    op.drop_column('commit', 'user_email')
    op.drop_column('commit', 'user_name')
