"""empty message

Revision ID: bd1848dcb9b1
Revises: 88401a56eeb4
Create Date: 2019-11-11 16:40:49.101120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd1848dcb9b1'
down_revision = '88401a56eeb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ATE',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gkgn_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('types', sa.String(length=100), nullable=True),
    sa.Column('region', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ATE')
    # ### end Alembic commands ###