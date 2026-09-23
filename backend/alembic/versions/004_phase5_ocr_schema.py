"""phase5 add ocr_results table

Revision ID: 004_phase5_ocr_schema
Revises: 003_phase4_object_detection_schema
Create Date: 2026-08-24 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_phase5_ocr_schema'
down_revision: Union[str, None] = '003_phase4_object_detection_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ocr_results table
    op.create_table(
        'ocr_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('normalized_text', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('line_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('x_min', sa.Float(), nullable=False),
        sa.Column('y_min', sa.Float(), nullable=False),
        sa.Column('x_max', sa.Float(), nullable=False),
        sa.Column('y_max', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ocr_results_id'), 'ocr_results', ['id'], unique=False)
    op.create_index(op.f('ix_ocr_results_analysis_run_id'), 'ocr_results', ['analysis_run_id'], unique=False)
    op.create_index(op.f('ix_ocr_results_company_id'), 'ocr_results', ['company_id'], unique=False)
    op.create_index(op.f('ix_ocr_results_created_at'), 'ocr_results', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ocr_results_created_at'), table_name='ocr_results')
    op.drop_index(op.f('ix_ocr_results_company_id'), table_name='ocr_results')
    op.drop_index(op.f('ix_ocr_results_analysis_run_id'), table_name='ocr_results')
    op.drop_index(op.f('ix_ocr_results_id'), table_name='ocr_results')
    op.drop_table('ocr_results')
