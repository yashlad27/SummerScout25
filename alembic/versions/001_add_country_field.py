"""add country field

Revision ID: 001_add_country
Revises: 
Create Date: 2025-10-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_country'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add country column to jobs table
    op.add_column('jobs', sa.Column('country', sa.String(length=50), nullable=True, server_default='us'))
    op.create_index(op.f('ix_jobs_country'), 'jobs', ['country'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_jobs_country'), table_name='jobs')
    op.drop_column('jobs', 'country')
