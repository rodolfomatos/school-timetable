"""Add updated_at to schedule entities

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-02

Os modelos SQLAlchemy já declaravam ``updated_at`` em schedule_versions,
schedule_assignments, unavailabilities e disputes, mas a coluna nunca foi
criada. Isto fazia qualquer SELECT falhar com UndefinedColumnError.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLES = (
    'schedule_versions',
    'schedule_assignments',
    'unavailabilities',
    'disputes',
)


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(
            table,
            sa.Column(
                'updated_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=False,
            ),
        )


def downgrade() -> None:
    for table in _TABLES:
        op.drop_column(table, 'updated_at')
