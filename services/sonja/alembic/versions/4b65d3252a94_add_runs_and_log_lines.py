"""Add runs and log lines

Revision ID: 4b65d3252a94
Revises: 0b6b1ad29568
Create Date: 2022-05-12 20:24:32.547000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b65d3252a94'
down_revision = '0b6b1ad29568'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'run',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('started', sa.DateTime, nullable=False, index=True),
        sa.Column('status', sa.Enum, nullable=False),
        sa.Column('build_id', index=True)
    )

    op.create_table(
        'log_line',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('number', sa.Integer, nullable=False, index=True),
        sa.Column('time', sa.DateTime, nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('run_id', index=True)
    )


def downgrade():
    op.drop_table('run')
    op.drop_table('log_line')
