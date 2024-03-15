"""Rename config to steps column

Revision ID: 03ea2fc77d60
Revises: 2ac625753917
Create Date: 2023-02-05 08:36:19.456202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03ea2fc77d60'
down_revision = '2ac625753917'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('check', sa.Column('steps', sa.String(length=1024), nullable=True))
    op.drop_column('check', 'config')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('check', sa.Column('config', sa.VARCHAR(length=1024), autoincrement=False, nullable=True))
    op.drop_column('check', 'steps')
    # ### end Alembic commands ###