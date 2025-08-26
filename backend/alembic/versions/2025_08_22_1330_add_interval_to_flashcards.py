"""Add interval column to flashcards

Revision ID: 2025_08_22_1330
Revises: 
Create Date: 2025-08-22 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_08_22_1330'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add interval column to flashcards table with default value of 1
    op.add_column('flashcards', 
                 sa.Column('interval', sa.Integer(), 
                          server_default='1', 
                          nullable=False))


def downgrade():
    # Remove interval column from flashcards table
    op.drop_column('flashcards', 'interval')
