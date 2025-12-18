from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ViolationSchema(BaseModel):
    rule_id: str
    severity: str
    detected_value: Optional[str]
    expected_value: Optional[str]
    suggestion: Optional[str]

    class Config:
        from_attributes = True

class RunResponse(BaseModel):
    run_id: str
    status: str
    start_ts: datetime
    end_ts: Optional[datetime]
    token_cost: float
    violations: List[ViolationSchema] = []

    class Config:
        from_attributes = True
