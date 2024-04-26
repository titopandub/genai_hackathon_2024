"""Add routes to flat_chat

Revision ID: 9cbfd566c1f1
Revises: 0f25d63f1d67
Create Date: 2024-03-15 15:00:04.943853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cbfd566c1f1'
down_revision: Union[str, None] = '0f25d63f1d67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('flat_chat', sa.Column('route', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('flat_chat', 'route')
    # ### end Alembic commands ###