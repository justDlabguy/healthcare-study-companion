"""Add interval field to flashcards table

Revision ID: add_interval_to_flashcards
Revises: 
Create Date: 2025-08-22 13:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_interval_to_flashcards'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add interval column to flashcards table
    op.add_column('flashcards', 
                 sa.Column('interval', sa.Integer(), 
                          server_default='1', 
                          nullable=False))

def downgrade():
    # Remove interval column from flashcards table
    op.drop_column('flashcards', 'interval')
