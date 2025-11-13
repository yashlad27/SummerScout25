"""Remove remote column

Revision ID: 002
Revises: 001
Create Date: 2025-11-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Remove remote column from jobs table."""
    op.drop_column('jobs', 'remote')


def downgrade():
    """Add remote column back."""
    op.add_column('jobs', sa.Column('remote', sa.Boolean(), server_default='false', nullable=True))
