"""Add missing columns to flashcard_reviews

Revision ID: 2025_08_22_1630
Revises: 44a4cd61bd1e
Create Date: 2025-08-22 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2025_08_22_1630'
down_revision = '44a4cd61bd1e'
branch_labels = None
depends_on = None

def upgrade():
    # Add review_time column if it doesn't exist
    op.add_column('flashcard_reviews', 
                 sa.Column('review_time', sa.DateTime(), nullable=True, 
                          comment='When the review was submitted'))
    
    # Add review_count column if it doesn't exist
    op.add_column('flashcard_reviews',
                 sa.Column('review_count', sa.Integer(), nullable=True,
                          server_default='0', comment='Number of times reviewed'))
    
    # Update existing rows to have default values
    op.execute("""
        UPDATE flashcard_reviews 
        SET review_time = NOW(), 
            review_count = 1
        WHERE review_time IS NULL
    """)
    
    # Make columns NOT NULL after setting defaults
    op.alter_column('flashcard_reviews', 'review_time', existing_type=sa.DateTime(),
                   nullable=False, existing_comment='When the review was submitted')
    op.alter_column('flashcard_reviews', 'review_count', existing_type=sa.Integer(),
                   nullable=False, existing_comment='Number of times reviewed')

def downgrade():
    # Drop the columns if they exist
    op.drop_column('flashcard_reviews', 'review_count')
    op.drop_column('flashcard_reviews', 'review_time')
