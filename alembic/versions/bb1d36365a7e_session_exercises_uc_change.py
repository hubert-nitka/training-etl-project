"""session_exercises_UC_change

Revision ID: bb1d36365a7e
Revises: 9671547d7bc0
Create Date: 2026-04-14 18:35:46.784535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb1d36365a7e'
down_revision: Union[str, Sequence[str], None] = '9671547d7bc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('only_one_exercise_per_session', 'session_exercises')
    op.create_unique_constraint('only_one_exercise_per_set_per_session', 'session_exercises', ['session_id','exercise_id','set_number'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('only_one_exercise_per_set_per_session', 'session_exercises')
    op.create_unique_constraint('only_one_exercise_per_session', 'session_exercises', ['session_id','exercise_id'])
