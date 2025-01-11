"""Your migration message

Revision ID: 45241f063d8a
Revises: 3d21edff714f
Create Date: 2025-01-08 17:16:37.979691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45241f063d8a'
down_revision: Union[str, None] = '3d21edff714f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'medias', 'posts', ['post_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'medias', type_='foreignkey')
    # ### end Alembic commands ###
