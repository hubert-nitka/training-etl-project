"""modify_session_exercises_table_for_descending_series

Revision ID: 9671547d7bc0
Revises: 9e459685a16a
Create Date: 2026-04-14 18:24:21.038881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9671547d7bc0'
down_revision: Union[str, Sequence[str], None] = '9e459685a16a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('session_exercises','working_set_number')
    op.add_column('session_exercises', sa.Column('set_number', sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column('session_exercises','set_number')
    op.add_column('session_exercises', sa.Column('working_set_number', sa.Integer, nullable=True))
