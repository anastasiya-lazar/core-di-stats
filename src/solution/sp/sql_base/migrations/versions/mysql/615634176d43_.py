"""empty message

Revision ID: 615634176d43
Revises: b7f720fee265
Create Date: 2022-09-30 09:00:02.518016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '615634176d43'
down_revision = 'b7f720fee265'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ingestion_request_status', sa.Column('subscriber_name', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ingestion_request_status', 'subscriber_name')
    # ### end Alembic commands ###