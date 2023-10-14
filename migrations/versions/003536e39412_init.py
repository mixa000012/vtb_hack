"""init

Revision ID: 003536e39412
Revises: df5a2fdf5dc7
Create Date: 2023-10-14 01:16:44.168833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003536e39412'
down_revision = 'df5a2fdf5dc7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('offices', sa.Column('network', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('offices', 'network')
    # ### end Alembic commands ###