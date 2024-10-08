"""empty message

Revision ID: d4be30465cef
Revises: a5e25dd6bdc3
Create Date: 2022-10-18 06:16:43.988797

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd4be30465cef'
down_revision = 'a5e25dd6bdc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ingestion_request_filter', 'condition',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=64),
               existing_nullable=True)
    op.alter_column('ingestion_request_status', 'subscriber_name',
               existing_type=mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'),
               type_=sa.JSON(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ingestion_request_status', 'subscriber_name',
               existing_type=sa.JSON(),
               type_=mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'),
               existing_nullable=True)
    op.alter_column('ingestion_request_filter', 'condition',
               existing_type=sa.String(length=64),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    # ### end Alembic commands ###
