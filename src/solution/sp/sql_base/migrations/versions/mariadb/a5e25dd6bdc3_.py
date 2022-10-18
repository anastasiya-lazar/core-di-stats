"""empty message

Revision ID: a5e25dd6bdc3
Revises: 359348b1b2f6
Create Date: 2022-10-17 12:43:28.824621

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a5e25dd6bdc3'
down_revision = '359348b1b2f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ingestion_request_status', 'subscriber_name',
               existing_type=mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'),
               type_=sa.JSON(),
               existing_nullable=True)
    op.alter_column('ingestion_status', 'request_id',
               existing_type=mysql.VARCHAR(length=128),
               nullable=False)
    op.alter_column('ingestion_status', 'source_id',
               existing_type=mysql.VARCHAR(length=128),
               nullable=False)
    op.drop_column('ingestion_status', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ingestion_status', sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False))
    op.alter_column('ingestion_status', 'source_id',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
    op.alter_column('ingestion_status', 'request_id',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
    op.alter_column('ingestion_request_status', 'subscriber_name',
               existing_type=sa.JSON(),
               type_=mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'),
               existing_nullable=True)
    # ### end Alembic commands ###