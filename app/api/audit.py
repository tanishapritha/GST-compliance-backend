from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.models import AuditLog

router = APIRouter()

@router.get("/runs/{run_id}", response_model=None) # Returning raw dict or schema
def get_audit_logs(
    run_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_admin)
) -> Any:
    return db.query(AuditLog).filter(AuditLog.run_id == run_id).all()
