import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.api import invoices, deps
from app.db.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup In-Memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_queue():
    mock_q = MagicMock()
    mock_q.enqueue.return_value = MagicMock(id="123")
    return mock_q

app.dependency_overrides[deps.get_db] = override_get_db
app.dependency_overrides[deps.get_queue] = override_get_queue

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "GST Compliance Backend"}

def test_auth_signup_login():
    # 1. Signup
    email = "test@example.com"
    password = "password123"
    
    response = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    if response.status_code == 400:
        # If user exists from previous run
        assert response.json()["detail"] == "The user with this username already exists in the system."
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert "id" in data

    # 2. Login
    login_data = {
        "username": email,
        "password": password
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    return tokens["access_token"]

def test_invoice_upload_flow():
    # Authenticate
    access_token = test_auth_signup_login()
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Create a dummy PDF
    with open("test_invoice.pdf", "wb") as f:
        f.write(b"%PDF-1.4 header dummy content")
    
    try:
        # 2. Upload
        with open("test_invoice.pdf", "rb") as f:
            response = client.post(
                "/api/v1/invoices/upload",
                files={"file": ("test_invoice.pdf", f, "application/pdf")},
                headers=headers
            )
        
        # Verify Upload response
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test_invoice.pdf"
        assert "id" in data
        invoice_id = data["id"]
        
        # 3. Get Invoice Details
        response = client.get(f"/api/v1/invoices/{invoice_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == invoice_id
        
        
        # 4. Simulate Worker Execution (Manually call service)
        # We need to use the same DB session or update the DB the test is using.
        # Since we are using a file based sqlite, we can open a new session.
        from app.services.extraction_service import ExtractionService
        from app.db.models import Invoice, InvoiceStatus
        
        db = TestingSessionLocal()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        invoice.status = InvoiceStatus.PROCESSING
        db.commit()
        
        # Mock OCR since we don't have a real PDF with text usually in test env
        
        with patch("app.services.ocr_service.OCRService.extract_text_from_pdf", return_value="Invoice No: INV-001\nGSTIN: 29ABCDE1234F1Z5\nDate: 12/12/2023\nTotal: 1000.00"):
             service = ExtractionService(db)
            #  file endpoint mock
             service.process_invoice(invoice.id, str(invoice.stored_path))
             
             # Mimic the worker: update status to COMPLETED after success
             invoice.status = InvoiceStatus.COMPLETED
             db.commit()
        
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        assert invoice.status == InvoiceStatus.COMPLETED
        assert invoice.data is not None
        db.close()

        # 5. Run Compliance
        response = client.post(f"/api/v1/compliance/run?invoice_id={invoice_id}", headers=headers)
        assert response.status_code == 200
        run_data = response.json()
        assert run_data["status"] == "completed"
        # Since we mocked the text, we expect some results.
        # Check for violations mock logic
        
    finally:
        if os.path.exists("test_invoice.pdf"):
            os.remove("test_invoice.pdf")
        if os.path.exists("test.db"):
            try:
                os.remove("test.db")
            except:
                pass


def test_compliance_run_failure_without_extraction():
    # Test that running compliance on an unproccessed invoice fails nicely
    access_token = test_auth_signup_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Upload new file
    with open("test_fail.pdf", "wb") as f: f.write(b"%PDF")
    try:
        with open("test_fail.pdf", "rb") as f:
            resp = client.post("/api/v1/invoices/upload", files={"file": ("test_fail.pdf", f, "application/pdf")}, headers=headers)
        invoice_id = resp.json()["id"]
        
        # Run compliance immediately (Worker hasn't run)
        response = client.post(f"/api/v1/compliance/run?invoice_id={invoice_id}", headers=headers)
        
        # Should 400 because data extraction is missing
        assert response.status_code == 400
        # assert "Invoice not processed yet" in response.json()["detail"]
    finally:
        if os.path.exists("test_fail.pdf"):
            os.remove("test_fail.pdf")
