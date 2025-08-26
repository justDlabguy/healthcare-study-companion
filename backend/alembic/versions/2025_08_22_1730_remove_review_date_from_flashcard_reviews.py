"""Remove review_date from flashcard_reviews

Revision ID: 2025_08_22_1730
Revises: 2025_08_22_1630
Create Date: 2025-08-22 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2025_08_22_1730'
down_revision = '2025_08_22_1630'
branch_labels = None
depends_on = None

def upgrade():
    # Check if the column exists before trying to drop it
    conn = op.get_bind()
    inspector = sa.inspect(conn.engine)
    columns = [col['name'] for col in inspector.get_columns('flashcard_reviews')]
    
    if 'review_date' in columns:
        op.drop_column('flashcard_reviews', 'review_date')

def downgrade():
    # Add the column back if rolling back
    op.add_column('flashcard_reviews',
                 sa.Column('review_date', sa.DateTime(), nullable=True,
                          comment='Legacy column, use review_time instead'))
