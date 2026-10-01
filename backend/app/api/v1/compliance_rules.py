from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.compliance_rule import ComplianceRule, RuleType, RuleSeverity
from app.schemas.compliance import (
    ComplianceRuleCreate,
    ComplianceRuleUpdate,
    ComplianceRuleResponse
)
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/compliance-rules", tags=["Compliance Rules"])


@router.post("", response_model=ComplianceRuleResponse, status_code=status.HTTP_201_CREATED)
def create_compliance_rule(
    payload: ComplianceRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Creates a new compliance rule for company or specific store (ADMIN/MANAGER)."""
    if payload.store_id:
        store = db.query(Store).filter(
            Store.id == payload.store_id,
            Store.company_id == current_user.company_id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found."
            )

    rule = ComplianceRule(
        company_id=current_user.company_id,
        store_id=payload.store_id,
        created_by=current_user.id,
        name=payload.name,
        description=payload.description,
        rule_type=payload.rule_type,
        severity=payload.severity,
        configuration=payload.configuration,
        is_active=payload.is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("", response_model=List[ComplianceRuleResponse])
def list_compliance_rules(
    store_id: Optional[UUID] = Query(None, description="Filter by store ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists compliance rules for current user's company tenant."""
    query = db.query(ComplianceRule).filter(ComplianceRule.company_id == current_user.company_id)

    if store_id:
        store = db.query(Store).filter(
            Store.id == store_id,
            Store.company_id == current_user.company_id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found."
            )
        query = query.filter((ComplianceRule.store_id == store_id) | (ComplianceRule.store_id == None))

    if is_active is not None:
        query = query.filter(ComplianceRule.is_active == is_active)

    return query.order_by(ComplianceRule.created_at.desc()).all()


@router.get("/{rule_id}", response_model=ComplianceRuleResponse)
def get_compliance_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves a compliance rule by ID enforcing company tenant isolation."""
    rule = db.query(ComplianceRule).filter(
        ComplianceRule.id == rule_id,
        ComplianceRule.company_id == current_user.company_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance rule not found."
        )

    return rule


@router.put("/{rule_id}", response_model=ComplianceRuleResponse)
def update_compliance_rule(
    rule_id: UUID,
    payload: ComplianceRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Updates a compliance rule (ADMIN/MANAGER)."""
    rule = db.query(ComplianceRule).filter(
        ComplianceRule.id == rule_id,
        ComplianceRule.company_id == current_user.company_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance rule not found."
        )

    if payload.name is not None:
        rule.name = payload.name
    if payload.description is not None:
        rule.description = payload.description
    if payload.rule_type is not None:
        rule.rule_type = payload.rule_type
    if payload.severity is not None:
        rule.severity = payload.severity
    if payload.configuration is not None:
        rule.configuration = payload.configuration
    if payload.is_active is not None:
        rule.is_active = payload.is_active
    if payload.store_id is not None:
        rule.store_id = payload.store_id

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_compliance_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Deletes a compliance rule (ADMIN/MANAGER)."""
    rule = db.query(ComplianceRule).filter(
        ComplianceRule.id == rule_id,
        ComplianceRule.company_id == current_user.company_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance rule not found."
        )

    db.delete(rule)
    db.commit()
    return None
