"""baseline

Revision ID: 02899ec9feeb
Revises: 531496a2ad76
Create Date: 2026-03-20 09:18:44.512324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02899ec9feeb'
down_revision: Union[str, Sequence[str], None] = '531496a2ad76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
