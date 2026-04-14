"""remove_planned_weight_column

Revision ID: 9e459685a16a
Revises: 78b9bb87e86d
Create Date: 2026-04-14 17:22:21.652046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e459685a16a'
down_revision: Union[str, Sequence[str], None] = '78b9bb87e86d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('plan_exercises','planned_weight')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('plan_exercises',
        sa.Column('planned_weight', sa.Numeric(5, 2), nullable=True)
    )
