"""init

Revision ID: cfd11e8f0eb7
Revises: 
Create Date: 2023-10-14 00:37:07.060862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd11e8f0eb7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('offices',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('salePointName', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('openHours', sa.JSON(), nullable=True),
    sa.Column('rko', sa.String(), nullable=True),
    sa.Column('openHoursIndividual', sa.JSON(), nullable=True),
    sa.Column('officeType', sa.String(), nullable=True),
    sa.Column('salePointFormat', sa.String(), nullable=True),
    sa.Column('suoAvailability', sa.String(), nullable=True),
    sa.Column('hasRamp', sa.String(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('metroStation', sa.String(), nullable=True),
    sa.Column('distance', sa.Integer(), nullable=True),
    sa.Column('kep', sa.Boolean(), nullable=True),
    sa.Column('myBranch', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('offices')
    # ### end Alembic commands ###