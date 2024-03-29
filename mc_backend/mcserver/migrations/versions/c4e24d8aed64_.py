"""empty message

Revision ID: c4e24d8aed64
Revises: bde9f5b4e88d
Create Date: 2018-12-05 09:40:08.357418

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from mcserver.app.models import ResourceType

# revision identifiers, used by Alembic.
revision = 'c4e24d8aed64'
down_revision = 'bde9f5b4e88d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("UpdateInfo")
    op.create_table('UpdateInfo', sa.Column('resource_type', sa.String(), primary_key=True),
                    sa.Column('created_time', sa.DateTime, default=datetime.utcnow, index=True),
                    sa.Column('last_modified_time', sa.DateTime, default=datetime.utcnow, index=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("UpdateInfo")
    op.execute("DROP TYPE resourcetype CASCADE")
    op.create_table('UpdateInfo', sa.Column('resource_type', sa.Enum(ResourceType), primary_key=True),
                    sa.Column('created_time', sa.DateTime, default=datetime.utcnow, index=True),
                    sa.Column('last_modified_time', sa.DateTime, default=datetime.utcnow, index=True))
    # ### end Alembic commands ###
