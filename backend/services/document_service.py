import fitz  # PyMuPDF
from typing import List

class DocumentService:
    """Service to handle document parsing and text manipulation."""
    
    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        """Extracts all raw text from a PDF file."""
        text = ""
        try:
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            raise
        return text
