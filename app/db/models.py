from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
import enum

class Base(DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class InvoiceStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class RunStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="owner")
    runs = relationship("Run", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    invoice_hash = Column(String, index=True)
    status = Column(String, default=InvoiceStatus.UPLOADED)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="invoices")
    data = relationship("InvoiceData", uselist=False, back_populates="invoice")
    runs = relationship("Run", back_populates="invoice")

class InvoiceData(Base):
    __tablename__ = "invoice_data"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    extracted_json = Column(JSON, nullable=True)
    extracted_text = Column(Text, nullable=True)
    extraction_quality = Column(Float, nullable=True) # 0.0 to 1.0

    invoice = relationship("Invoice", back_populates="data")

class Rule(Base):
    __tablename__ = "rules"

    rule_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String) # low, medium, high
    check_type = Column(String) # regex, calculation, presence
    meta = Column(JSON) # Config for the rule

class Run(Base):
    __tablename__ = "runs"

    run_id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(Integer, ForeignKey("users.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    status = Column(String, default=RunStatus.RUNNING)
    start_ts = Column(DateTime, default=datetime.utcnow)
    end_ts = Column(DateTime, nullable=True)
    token_cost = Column(Float, default=0.0)

    user = relationship("User", back_populates="runs")
    invoice = relationship("Invoice", back_populates="runs")
    violations = relationship("Violation", back_populates="run")

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.run_id"))
    rule_id = Column(String, ForeignKey("rules.rule_id"))
    detected_value = Column(String, nullable=True)
    expected_value = Column(String, nullable=True)
    suggestion = Column(Text, nullable=True)
    severity = Column(String)

    run = relationship("Run", back_populates="violations")
    rule = relationship("Rule")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String)
    event = Column(String)
    payload_hash = Column(String, nullable=True)
    response_hash = Column(String, nullable=True)
    token_cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
