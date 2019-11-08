"""gkgn init

Revision ID: 88401a56eeb4
Revises: 
Create Date: 2019-11-08 12:53:38.429519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88401a56eeb4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('settlement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gkgn_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('types', sa.String(length=100), nullable=True),
    sa.Column('region', sa.String(length=256), nullable=True),
    sa.Column('district', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('settlement')
    # ### end Alembic commands ###
