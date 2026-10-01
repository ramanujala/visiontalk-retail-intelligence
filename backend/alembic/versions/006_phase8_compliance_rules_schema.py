"""phase8 add compliance_rules and compliance_findings tables

Revision ID: 006_phase8_compliance_rules_schema
Revises: 005_phase7_expected_actual_schema
Create Date: 2026-10-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '006_phase8_compliance_rules_schema'
down_revision: Union[str, None] = '005_phase7_expected_actual_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create compliance_rules table
    op.create_table(
        'compliance_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_rules_id'), 'compliance_rules', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_rules_company_id'), 'compliance_rules', ['company_id'], unique=False)
    op.create_index(op.f('ix_compliance_rules_store_id'), 'compliance_rules', ['store_id'], unique=False)
    op.create_index(op.f('ix_compliance_rules_created_by'), 'compliance_rules', ['created_by'], unique=False)
    op.create_index(op.f('ix_compliance_rules_rule_type'), 'compliance_rules', ['rule_type'], unique=False)
    op.create_index(op.f('ix_compliance_rules_severity'), 'compliance_rules', ['severity'], unique=False)
    op.create_index(op.f('ix_compliance_rules_is_active'), 'compliance_rules', ['is_active'], unique=False)
    op.create_index(op.f('ix_compliance_rules_created_at'), 'compliance_rules', ['created_at'], unique=False)

    # 2. Create compliance_findings table
    op.create_table(
        'compliance_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('evidence_references', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rule_id'], ['compliance_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_findings_id'), 'compliance_findings', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_company_id'), 'compliance_findings', ['company_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_store_id'), 'compliance_findings', ['store_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_image_id'), 'compliance_findings', ['image_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_analysis_run_id'), 'compliance_findings', ['analysis_run_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_rule_id'), 'compliance_findings', ['rule_id'], unique=False)
    op.create_index(op.f('ix_compliance_findings_status'), 'compliance_findings', ['status'], unique=False)
    op.create_index(op.f('ix_compliance_findings_severity'), 'compliance_findings', ['severity'], unique=False)
    op.create_index(op.f('ix_compliance_findings_created_at'), 'compliance_findings', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('compliance_findings')
    op.drop_table('compliance_rules')
