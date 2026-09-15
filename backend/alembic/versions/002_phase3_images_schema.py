"""phase3 add images table

Revision ID: 002_phase3_images_schema
Revises: 001_phase2_initial_schema
Create Date: 2026-08-22 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_phase3_images_schema'
down_revision: Union[str, None] = '001_phase2_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_key', sa.String(length=512), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('quality_score', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('quality_flags', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_id'), 'images', ['id'], unique=False)
    op.create_index(op.f('ix_images_company_id'), 'images', ['company_id'], unique=False)
    op.create_index(op.f('ix_images_store_id'), 'images', ['store_id'], unique=False)
    op.create_index(op.f('ix_images_uploaded_by'), 'images', ['uploaded_by'], unique=False)
    op.create_index(op.f('ix_images_status'), 'images', ['status'], unique=False)
    op.create_index(op.f('ix_images_created_at'), 'images', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_images_created_at'), table_name='images')
    op.drop_index(op.f('ix_images_status'), table_name='images')
    op.drop_index(op.f('ix_images_uploaded_by'), table_name='images')
    op.drop_index(op.f('ix_images_store_id'), table_name='images')
    op.drop_index(op.f('ix_images_company_id'), table_name='images')
    op.drop_index(op.f('ix_images_id'), table_name='images')
    op.drop_table('images')
