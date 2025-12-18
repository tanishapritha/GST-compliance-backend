from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.db.models import Run, Invoice, User, RunStatus
from app.schemas.compliance import RunResponse
from app.services.compliance_engine import ComplianceEngine
import uuid

router = APIRouter()

@router.post("/run", response_model=RunResponse)
def run_compliance(
    invoice_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if not invoice.data:
         raise HTTPException(status_code=400, detail="Invoice not processed yet. Wait for ingestion.")

    # Create Run
    run_id = str(uuid.uuid4())
    run = Run(
        run_id=run_id,
        user_id=current_user.id,
        invoice_id=invoice.id,
        status=RunStatus.RUNNING
    )
    db.add(run)
    db.commit()
    
    # Execute Compliance Engine (Synchronous for MVP simplicity, could be backgrounded)
    engine = ComplianceEngine(db)
    engine.run_compliance_checks(run, invoice.data.extracted_json)
    
    db.refresh(run)
    return run

@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(
    run_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    run = db.query(Run).filter(Run.run_id == run_id, Run.user_id == current_user.id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
