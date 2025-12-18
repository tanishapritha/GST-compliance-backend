from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class InvoiceBase(BaseModel):
    filename: str

class InvoiceResponse(InvoiceBase):
    id: int
    user_id: int
    status: str
    invoice_hash: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class InvoiceDetail(InvoiceResponse):
    extracted_data: Optional[Dict[str, Any]] = None
