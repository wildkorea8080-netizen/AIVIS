"""add project owner token and soft delete

Revision ID: 4d5d35b7e3bc
Revises: 164211f86fd5
Create Date: 2026-09-09 14:28:23.181337

"""
from typing import Sequence, Union

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d5d35b7e3bc'
down_revision: Union[str, None] = '164211f86fd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('monitor_projects', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # 기존 행이 있으므로 곧바로 NOT NULL을 걸 수 없다.
    # nullable로 추가 -> 행마다 서로 다른 UUID로 백필 -> NOT NULL + unique 인덱스.
    op.add_column('monitor_projects', sa.Column('owner_token', sa.String(length=36), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM monitor_projects WHERE owner_token IS NULL")).fetchall()
    for (project_id,) in rows:
        conn.execute(
            sa.text("UPDATE monitor_projects SET owner_token = :token WHERE id = :id"),
            {"token": str(uuid4()), "id": project_id},
        )

    op.alter_column('monitor_projects', 'owner_token', nullable=False)
    op.create_index(op.f('ix_monitor_projects_owner_token'), 'monitor_projects', ['owner_token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_monitor_projects_owner_token'), table_name='monitor_projects')
    op.drop_column('monitor_projects', 'deleted_at')
    op.drop_column('monitor_projects', 'owner_token')
