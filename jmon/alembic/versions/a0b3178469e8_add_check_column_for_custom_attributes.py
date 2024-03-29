"""Add check column for custom attributes

Revision ID: a0b3178469e8
Revises: e686a7f6dfc1
Create Date: 2023-08-11 06:05:42.957083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0b3178469e8'
down_revision = 'e686a7f6dfc1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('check', sa.Column('attributes', sa.String(length=1024), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('check', 'attributes')
    # ### end Alembic commands ###
