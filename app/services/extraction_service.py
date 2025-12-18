from sqlalchemy.orm import Session
from app.db.models import InvoiceData
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService

class ExtractionService:
    def __init__(self, db: Session):
        self.db = db
        self.ocr = OCRService()
        self.llm = LLMService()

    def process_invoice(self, invoice_id: int, file_path: str):
        # 1. OCR
        text = self.ocr.extract_text_from_pdf(file_path)
        
        # 2. LLM / Extraction
        extracted_data = self.llm.parse_invoice_text(text)
        
        # 3. Store
        invoice_data = InvoiceData(
            invoice_id=invoice_id,
            extracted_text=text,
            extracted_json=extracted_data,
            extraction_quality=0.85 # Mock quality score
        )
        self.db.add(invoice_data)
        self.db.commit()
        self.db.refresh(invoice_data)
        return invoice_data
