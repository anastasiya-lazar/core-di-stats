"""empty message

Revision ID: a90bf87a3ccd
Revises: 82c2737ed204
Create Date: 2022-10-17 12:43:00.802804

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a90bf87a3ccd'
down_revision = '82c2737ed204'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    op.add_column('ingestion_status', sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False))
    op.alter_column('ingestion_status', 'source_id',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
    op.alter_column('ingestion_status', 'request_id',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
    # ### end Alembic commands ###
