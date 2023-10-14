"""add credits

Revision ID: c7f48541b239
Revises: 3f577bb313a9
Create Date: 2023-10-14 14:14:16.546648

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7f48541b239'
down_revision = '3f577bb313a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('offices', sa.Column('consultation', sa.Boolean(), nullable=True))
    op.drop_column('offices', 'Consultation')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('offices', sa.Column('Consultation', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('offices', 'consultation')
    # ### end Alembic commands ###
