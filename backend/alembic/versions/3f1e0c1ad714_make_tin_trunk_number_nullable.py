"""Make tin_trunk_number nullable

Revision ID: 3f1e0c1ad714
Revises: 
Create Date: 2025-05-02 18:37:17.563734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f1e0c1ad714'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use raw SQL to modify the column
    op.execute("ALTER TABLE admin_managers MODIFY COLUMN tin_trunk_number VARCHAR(50) NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert the change if needed
    op.execute("ALTER TABLE admin_managers MODIFY COLUMN tin_trunk_number VARCHAR(50) NOT NULL")
