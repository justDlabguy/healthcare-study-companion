"""merge heads

Revision ID: 44a4cd61bd1e
Revises: 2025_08_22_1330, 83cdad67b5e6, add_interval_to_flashcards
Create Date: 2025-08-22 15:08:59.179771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44a4cd61bd1e'
down_revision: Union[str, None] = ('2025_08_22_1330', '83cdad67b5e6', 'add_interval_to_flashcards')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
