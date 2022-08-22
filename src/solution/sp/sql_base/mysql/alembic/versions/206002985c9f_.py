"""empty message

Revision ID: 206002985c9f
Revises: 
Create Date: 2022-08-19 14:13:39.852067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '206002985c9f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingestion_status',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('request_id', sa.String(length=128), nullable=True),
    sa.Column('source_id', sa.String(length=128), nullable=True),
    sa.Column('file_uri', sa.String(length=256), nullable=True),
    sa.Column('entity_type', sa.String(length=80), nullable=True),
    sa.Column('status', sa.String(length=80), nullable=True),
    sa.Column('is_error', sa.Boolean(), nullable=True),
    sa.Column('message', sa.String(length=256), nullable=True),
    sa.Column('total_record_count', sa.Integer(), nullable=True),
    sa.Column('total_failed_count', sa.Integer(), nullable=True),
    sa.Column('total_success_count', sa.Integer(), nullable=True),
    sa.Column('source_queue_name', sa.String(length=256), nullable=True),
    sa.Column('last_stat_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['request_id'], ['ingestion_request_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscriber_ingestion_status',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('request_id', sa.String(length=128), nullable=True),
    sa.Column('source_id', sa.String(length=128), nullable=True),
    sa.Column('file_uri', sa.String(length=256), nullable=True),
    sa.Column('subscriber', sa.String(length=128), nullable=True),
    sa.Column('status', sa.String(length=80), nullable=True),
    sa.Column('is_error', sa.Boolean(), nullable=True),
    sa.Column('message', sa.String(length=256), nullable=True),
    sa.Column('total_record_count', sa.Integer(), nullable=True),
    sa.Column('total_failed_count', sa.Integer(), nullable=True),
    sa.Column('total_success_count', sa.Integer(), nullable=True),
    sa.Column('status_url', sa.String(length=256), nullable=True),
    sa.Column('last_stat_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['request_id'], ['ingestion_request_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriber_ingestion_status')
    op.drop_table('ingestion_status')
    # ### end Alembic commands ###
