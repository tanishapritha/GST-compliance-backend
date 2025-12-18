import json
import re

class LLMService:
    def parse_invoice_text(self, text: str) -> dict:
        """
        Abstraction for LLM.
        In a real scenario, this would call OpenAI/Anthropic/Gemini.
        Here, we mock the extraction with Regex or return a dummy structure 
        to ensure the app is runnable without API keys.
        """
        # Mock logic to extract potential GSTIN, Dates, and Amounts
        # This is a heuristic fallback since we don't have a live LLM key.
        
        data = {
            "invoice_number": self._extract_field(text, r"Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9/-]+)"),
            "gstin": self._extract_field(text, r"GSTIN\s*[:\-]?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})"),
            "date": self._extract_field(text, r"Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})"),
            "total_amount": self._extract_amount(text),
            "line_items": [] # Mock empty for now or try to parse
        }
        
        # Add basic line item if total found
        if data["total_amount"]:
             data["line_items"] = [
                 {
                     "description": "Service Charge",
                     "hsn_code": "998311",
                     "taxable_value": float(data["total_amount"]) * 0.82, # Mock reverse calc
                     "tax_rate": 18.0,
                     "tax_amount": float(data["total_amount"]) * 0.18
                 }
             ]
        
        return data

    def _extract_field(self, text, pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_amount(self, text):
        # Look for "Total" followed by number
        match = re.search(r"Total\s*[:\-]?\s*([\d,]+\.?\d{0,2})", text, re.IGNORECASE)
        if match:
             return match.group(1).replace(",", "")
        return "0.00"
