"""phase7 add expected_products, expected_actual_items, expected_actual_issues tables

Revision ID: 005_phase7_expected_actual_schema
Revises: 004_phase5_ocr_schema
Create Date: 2026-09-23 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '005_phase7_expected_actual_schema'
down_revision: Union[str, None] = '004_phase5_ocr_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create expected_products table
    op.create_table(
        'expected_products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('product_code', sa.String(length=100), nullable=False),
        sa.Column('expected_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('expected_min_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('expected_max_quantity', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'store_id', 'product_code', name='uix_company_store_product_code')
    )
    op.create_index(op.f('ix_expected_products_id'), 'expected_products', ['id'], unique=False)
    op.create_index(op.f('ix_expected_products_company_id'), 'expected_products', ['company_id'], unique=False)
    op.create_index(op.f('ix_expected_products_store_id'), 'expected_products', ['store_id'], unique=False)
    op.create_index(op.f('ix_expected_products_product_code'), 'expected_products', ['product_code'], unique=False)
    op.create_index(op.f('ix_expected_products_is_active'), 'expected_products', ['is_active'], unique=False)
    op.create_index(op.f('ix_expected_products_created_at'), 'expected_products', ['created_at'], unique=False)

    # 2. Create expected_actual_items table
    op.create_table(
        'expected_actual_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expected_product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('product_code', sa.String(length=100), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('expected_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expected_min_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expected_max_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('observed_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('difference', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('evidence_references', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expected_product_id'], ['expected_products.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expected_actual_items_id'), 'expected_actual_items', ['id'], unique=False)
    op.create_index(op.f('ix_expected_actual_items_analysis_run_id'), 'expected_actual_items', ['analysis_run_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_items_company_id'), 'expected_actual_items', ['company_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_items_expected_product_id'), 'expected_actual_items', ['expected_product_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_items_status'), 'expected_actual_items', ['status'], unique=False)
    op.create_index(op.f('ix_expected_actual_items_created_at'), 'expected_actual_items', ['created_at'], unique=False)

    # 3. Create expected_actual_issues table
    op.create_table(
        'expected_actual_issues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expected_product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('issue_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('evidence_references', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expected_product_id'], ['expected_products.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expected_actual_issues_id'), 'expected_actual_issues', ['id'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_analysis_run_id'), 'expected_actual_issues', ['analysis_run_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_company_id'), 'expected_actual_issues', ['company_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_store_id'), 'expected_actual_issues', ['store_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_image_id'), 'expected_actual_issues', ['image_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_expected_product_id'), 'expected_actual_issues', ['expected_product_id'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_issue_type'), 'expected_actual_issues', ['issue_type'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_severity'), 'expected_actual_issues', ['severity'], unique=False)
    op.create_index(op.f('ix_expected_actual_issues_created_at'), 'expected_actual_issues', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('expected_actual_issues')
    op.drop_table('expected_actual_items')
    op.drop_table('expected_products')
