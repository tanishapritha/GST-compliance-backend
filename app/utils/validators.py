import re

class GSTValidator:
    GST_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

    @staticmethod
    def validate_gstin(gstin: str) -> bool:
        if not gstin:
            return False
        return bool(re.match(GSTValidator.GST_REGEX, gstin))
