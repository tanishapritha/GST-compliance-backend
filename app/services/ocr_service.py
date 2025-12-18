import pdfplumber

class OCRService:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        text_content = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
