from typing import Optional
from fastapi import Header, Query, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import Organization

def get_current_organization_id(
    x_org_id: Optional[str] = Header(None, alias="X-Organization-Id"),
    org_id: Optional[int] = Query(None, alias="org_id"),
    db: Session = Depends(get_db)
) -> int:
    """
    Extracts active organization ID from request header or query parameter.
    Validates that the organization exists, defaulting safely to Org 1 if invalid or absent.
    """
    candidate_id: Optional[int] = None
    if x_org_id and x_org_id.strip().isdigit():
        candidate_id = int(x_org_id.strip())
    elif org_id is not None and org_id > 0:
        candidate_id = org_id

    if candidate_id:
        exists = db.query(Organization.id).filter(Organization.id == candidate_id).scalar()
        if exists:
            return candidate_id

    # Fallback to organization 1 or first available
    first_org = db.query(Organization.id).order_by(Organization.id.asc()).first()
    if first_org:
        return first_org[0]
    return 1
