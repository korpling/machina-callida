"""empty message

Revision ID: 382b09e85c8b
Revises: 309cade7121b
Create Date: 2019-10-14 14:54:25.145226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '382b09e85c8b'
down_revision = '309cade7121b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Exercise', sa.Column('language', sa.String(), server_default='de', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Exercise', 'language')
    # ### end Alembic commands ###
