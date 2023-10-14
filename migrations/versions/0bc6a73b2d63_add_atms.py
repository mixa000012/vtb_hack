"""add atms

Revision ID: 0bc6a73b2d63
Revises: 003536e39412
Create Date: 2023-10-14 09:26:17.436087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bc6a73b2d63'
down_revision = '003536e39412'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('wheelchair', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('blind', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'blind')
    op.drop_column('users', 'wheelchair')
    # ### end Alembic commands ###
