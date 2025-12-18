from sqlalchemy.orm import Session
from app.db.models import AuditLog
import json

class AuditService:
    @staticmethod
    def log_event(db: Session, user_id: int, endpoint: str, event: str, payload: dict = None, response: dict = None):
        log = AuditLog(
            user_id=user_id,
            endpoint=endpoint,
            event=event,
            payload_hash=str(hash(json.dumps(payload))) if payload else None,
            response_hash=str(hash(json.dumps(response))) if response else None
        )
        db.add(log)
        db.commit()
