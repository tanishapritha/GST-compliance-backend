import shutil
import uuid
import os
from typing import List, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
from redis import Redis
from rq import Queue

from app.api import deps
from app.db.models import Invoice, User, InvoiceStatus, InvoiceData
from app.schemas.invoice import InvoiceResponse, InvoiceDetail
from app.core.config import settings
from app.utils.file_utils import FileUtils

# Redis Setup
try:
    redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, socket_connect_timeout=1)
    redis_conn.ping()
    q = Queue(connection=redis_conn)
except Exception as e:
    print(f"Warning: Redis not connected. Background tasks will fail. {e}")
    q = None

router = APIRouter()

@router.post("/upload", response_model=InvoiceResponse)
def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    q: Queue = Depends(deps.get_queue)
) -> Any:
    if not file.filename.endswith(".pdf"):

        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Save file
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{file.filename}"
    file_path = Path(settings.UPLOAD_FOLDER) / safe_filename
    
    FileUtils.save_upload_file(file, file_path)
    
    # Create DB Entry
    invoice = Invoice(
        user_id=current_user.id,
        filename=file.filename,
        stored_path=str(file_path),
        status=InvoiceStatus.UPLOADED
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Enqueue Job
    if q:
        from app.workers.ingestion_worker import process_invoice_job
        q.enqueue(process_invoice_job, invoice.id)
    else:
        print("Redis queue not available. Skipping background job.")

    return invoice

@router.get("/", response_model=List[InvoiceResponse])
def get_invoices(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return db.query(Invoice).filter(Invoice.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/{invoice_id}", response_model=InvoiceDetail)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Construct response with extracted data if available
    response = InvoiceDetail.from_orm(invoice)
    if invoice.data:
        response.extracted_data = invoice.data.extracted_json
    return response
