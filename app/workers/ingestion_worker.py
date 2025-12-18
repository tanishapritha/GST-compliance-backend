from app.db.session import SessionLocal
from app.services.extraction_service import ExtractionService
from app.db.models import Invoice, InvoiceStatus

def process_invoice_job(invoice_id: int):
    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return
        
        invoice.status = InvoiceStatus.PROCESSING
        db.commit()

        service = ExtractionService(db)
        try:
            service.process_invoice(invoice.id, invoice.stored_path)
            invoice.status = InvoiceStatus.COMPLETED
        except Exception as e:
            print(f"Extraction failed: {e}")
            invoice.status = InvoiceStatus.FAILED
        
        db.commit()
    finally:
        db.close()
