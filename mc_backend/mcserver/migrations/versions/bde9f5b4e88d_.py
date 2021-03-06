"""empty message

Revision ID: bde9f5b4e88d
Revises: 8ba6be1af780
Create Date: 2018-10-29 12:30:17.854759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bde9f5b4e88d'
down_revision = '8ba6be1af780'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Exercise', sa.Column('conll', sa.String(), server_default='', nullable=False))
    op.drop_column('Exercise', 'text')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Exercise', sa.Column('text', sa.VARCHAR(), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))
    op.drop_column('Exercise', 'conll')
    # ### end Alembic commands ###
