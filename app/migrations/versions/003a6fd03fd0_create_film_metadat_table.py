"""create film metadat table

Revision ID: 003a6fd03fd0
Revises: 9cbfd566c1f1
Create Date: 2024-04-15 13:49:56.379206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003a6fd03fd0'
down_revision: Union[str, None] = '9cbfd566c1f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('film_metadata',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('group_l1', sa.String(), nullable=True),
        sa.Column('group_l2', sa.String(), nullable=True),
        sa.Column('genres', sa.String(), nullable=True),
        sa.Column('actors', sa.String(), nullable=True),
        sa.Column('directors', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('release_date', sa.String(), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('age_rating', sa.String(), nullable=True),
        sa.Column('content_url', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('image_portrait', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('popularity', sa.String(), nullable=True),
        sa.Column('total_watchers', sa.Integer(), nullable=True),
        sa.Column('search_text', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('film_metadata')
