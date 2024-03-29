"""Add run index for check_id and timestamp

Revision ID: a76dadf5ab0e
Revises: 6f09a4a96533
Create Date: 2023-08-17 05:29:33.129466

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a76dadf5ab0e'
down_revision = '6f09a4a96533'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('check_timestamp', 'run', ['check_id', sa.text('timestamp ASC')], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('check_timestamp', table_name='run')
    # ### end Alembic commands ###
