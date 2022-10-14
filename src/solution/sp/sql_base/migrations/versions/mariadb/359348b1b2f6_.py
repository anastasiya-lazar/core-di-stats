"""empty message

Revision ID: 359348b1b2f6
Revises: 873cfd295608
Create Date: 2022-10-14 06:13:50.241269

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '359348b1b2f6'
down_revision = '873cfd295608'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ingestion_request_status', 'subscriber_name',
               existing_type=mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'),
               type_=sa.JSON(),
               existing_nullable=True)
    op.create_unique_constraint('request_source_uc', 'ingestion_status', ['request_id', 'source_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('request_source_uc', 'ingestion_status', type_='unique')
    op.alter_column('ingestion_request_status', 'subscriber_name',
               existing_type=sa.JSON(),
               type_=mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'),
               existing_nullable=True)
    # ### end Alembic commands ###