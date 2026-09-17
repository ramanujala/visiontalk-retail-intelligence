"""phase4 add analysis_runs and detections tables

Revision ID: 003_phase4_object_detection_schema
Revises: 002_phase3_images_schema
Create Date: 2026-08-23 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003_phase4_object_detection_schema'
down_revision: Union[str, None] = '002_phase3_images_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create analysis_runs table
    op.create_table(
        'analysis_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_runs_id'), 'analysis_runs', ['id'], unique=False)
    op.create_index(op.f('ix_analysis_runs_company_id'), 'analysis_runs', ['company_id'], unique=False)
    op.create_index(op.f('ix_analysis_runs_image_id'), 'analysis_runs', ['image_id'], unique=False)
    op.create_index(op.f('ix_analysis_runs_initiated_by'), 'analysis_runs', ['initiated_by'], unique=False)
    op.create_index(op.f('ix_analysis_runs_analysis_type'), 'analysis_runs', ['analysis_type'], unique=False)
    op.create_index(op.f('ix_analysis_runs_status'), 'analysis_runs', ['status'], unique=False)
    op.create_index(op.f('ix_analysis_runs_created_at'), 'analysis_runs', ['created_at'], unique=False)

    # 2. Create detections table
    op.create_table(
        'detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('class_name', sa.String(length=100), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('x_min', sa.Float(), nullable=False),
        sa.Column('y_min', sa.Float(), nullable=False),
        sa.Column('x_max', sa.Float(), nullable=False),
        sa.Column('y_max', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detections_id'), 'detections', ['id'], unique=False)
    op.create_index(op.f('ix_detections_analysis_run_id'), 'detections', ['analysis_run_id'], unique=False)
    op.create_index(op.f('ix_detections_company_id'), 'detections', ['company_id'], unique=False)
    op.create_index(op.f('ix_detections_class_name'), 'detections', ['class_name'], unique=False)
    op.create_index(op.f('ix_detections_created_at'), 'detections', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_detections_created_at'), table_name='detections')
    op.drop_index(op.f('ix_detections_class_name'), table_name='detections')
    op.drop_index(op.f('ix_detections_company_id'), table_name='detections')
    op.drop_index(op.f('ix_detections_analysis_run_id'), table_name='detections')
    op.drop_index(op.f('ix_detections_id'), table_name='detections')
    op.drop_table('detections')

    op.drop_index(op.f('ix_analysis_runs_created_at'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_status'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_analysis_type'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_initiated_by'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_image_id'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_company_id'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_id'), table_name='analysis_runs')
    op.drop_table('analysis_runs')
