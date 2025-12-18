from sqlalchemy.orm import Session
from app.db.models import Violation, Run, Rule, RunStatus
from app.utils.validators import GSTValidator
from datetime import datetime
import uuid

class ComplianceEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_compliance_checks(self, run: Run, data: dict):
        violations = []
        
        # Rule 1: GSTIN Presence
        if not data.get("gstin"):
            violations.append(self._create_violation(run.run_id, "RULE_001", "GSTIN Missing", "high", None, "Present", "Ensure GSTIN is clearly visible"))
        else:
            # Rule 2: GSTIN Format
            if not GSTValidator.validate_gstin(data.get("gstin")):
                violations.append(self._create_violation(run.run_id, "RULE_002", "Invalid GSTIN Format", "high", data.get("gstin"), "Valid Regex", "Check for typos in GSTIN"))

        # Rule 3: HSN Check
        items = data.get("line_items", [])
        hsn_missing = any(not item.get("hsn_code") for item in items)
        if hsn_missing:
            violations.append(self._create_violation(run.run_id, "RULE_003", "HSN Code Missing", "medium", "Missing", "Present", "Add HSN codes for all items"))

        # Rule 4: Tax Calculation
        # Simple check: Tax Amount ~ Taxable Value * Rate
        for idx, item in enumerate(items):
            try:
                taxable = float(item.get("taxable_value", 0))
                rate = float(item.get("tax_rate", 0))
                tax_amt = float(item.get("tax_amount", 0))
                
                expected_tax = taxable * (rate / 100)
                if abs(expected_tax - tax_amt) > 1.0: # 1 rupee tolerance
                    violations.append(self._create_violation(
                        run.run_id, 
                        "RULE_004", 
                        f"Tax Mismatch Item {idx+1}", 
                        "high", 
                        str(tax_amt), 
                        str(expected_tax), 
                        "Recalculate tax amount"
                    ))
            except (ValueError, TypeError):
                pass
        
        # Save violations
        if violations:
            self.db.add_all(violations)
        
        run.status = RunStatus.COMPLETED
        run.end_ts = datetime.utcnow()
        self.db.commit()

    def _create_violation(self, run_id, rule_id, rule_title, severity, detected, expected, suggestion):
        # Ensure rule exists (idempotent for demo)
        rule = self.db.query(Rule).filter(Rule.rule_id == rule_id).first()
        if not rule:
            rule = Rule(rule_id=rule_id, title=rule_title, severity=severity, check_type="standard")
            self.db.add(rule)
            self.db.commit()

        return Violation(
            run_id=run_id,
            rule_id=rule_id,
            detected_value=detected,
            expected_value=expected,
            suggestion=suggestion,
            severity=severity
        )
